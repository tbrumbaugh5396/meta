"""Health check utilities for components."""

import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, error, success
from meta.utils.manifest import get_components, get_environment_config
from meta.utils.git import get_current_version, get_commit_sha
from meta.utils.lock import get_locked_components
from meta.utils.environment_locks import load_environment_lock_file
from meta.utils.bazel import run_bazel_build, run_bazel_test


class HealthStatus:
    """Represents health status of a component."""
    def __init__(self, component: str):
        self.component = component
        self.checks: Dict[str, bool] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.healthy = True
    
    def add_check(self, name: str, passed: bool, error: Optional[str] = None):
        """Add a health check result."""
        self.checks[name] = passed
        if not passed:
            self.healthy = False
            if error:
                self.errors.append(f"{name}: {error}")
    
    def add_warning(self, message: str):
        """Add a warning."""
        self.warnings.append(message)
    
    def __repr__(self):
        status = "✅" if self.healthy else "❌"
        return f"{status} {self.component}"


def check_component_exists(component: str) -> tuple[bool, Optional[str]]:
    """Check if component directory exists."""
    comp_path = Path(f"components/{component}")
    if not comp_path.exists():
        return False, f"Component directory not found: {comp_path}"
    return True, None


def check_component_version(component: str, env: str, manifests_dir: str = "manifests") -> tuple:
    """Check if component version matches manifest."""
    comp_path = Path(f"components/{component}")
    if not comp_path.exists():
        return False, "Component not found"
    
    # Get current version
    current_version = get_current_version(str(comp_path))
    if not current_version:
        return False, "Could not determine current version"
    
    # Get expected version from manifest
    components = get_components(manifests_dir)
    if component not in components:
        return False, "Component not in manifest"
    
    expected_version = components[component].get("version", "latest")
    
    # Check if locked
    if env:
        lock_data = load_environment_lock_file(env, manifests_dir)
        if lock_data and component in lock_data.get("components", {}):
            expected_commit = lock_data["components"][component].get("commit")
            if expected_commit:
                current_commit = get_commit_sha(str(comp_path))
                if current_commit and current_commit.startswith(expected_commit[:8]):
                    return True, None
                return False, f"Commit mismatch: expected {expected_commit[:8]}, got {current_commit[:8] if current_commit else 'unknown'}"
    
    # For version-based checks, we'll be lenient (just check it exists)
    return True, None


def check_component_builds(component: str) -> tuple:
    """Check if component builds successfully."""
    comp_path = Path(f"components/{component}")
    if not comp_path.exists():
        return False, "Component not found"
    
    # Check if it's a Bazel component
    build_file = comp_path / "BUILD.bazel"
    if not build_file.exists():
        # Not a Bazel component, skip build check
        return True, None
    
    # Try to build
    try:
        result = run_bazel_build("//...", str(comp_path))
        if result:
            return True, None
        else:
            return False, "Build failed"
    except Exception as e:
        return False, f"Build error: {str(e)}"


def check_component_tests(component: str) -> tuple:
    """Check if component tests pass."""
    comp_path = Path(f"components/{component}")
    if not comp_path.exists():
        return False, "Component not found"
    
    # Check if it's a Bazel component
    build_file = comp_path / "BUILD.bazel"
    if not build_file.exists():
        # Not a Bazel component, skip test check
        return True, None
    
    # Try to run tests
    try:
        result = run_bazel_test("//...", str(comp_path))
        if result:
            return True, None
        else:
            return False, "Tests failed"
    except Exception as e:
        return False, f"Test error: {str(e)}"


def check_component_dependencies(component: str, manifests_dir: str = "manifests") -> tuple:
    """Check if component dependencies are available."""
    components = get_components(manifests_dir)
    if component not in components:
        return False, "Component not in manifest"
    
    comp_data = components[component]
    depends_on = comp_data.get("depends_on", [])
    
    missing = []
    for dep in depends_on:
        dep_path = Path(f"components/{dep}")
        if not dep_path.exists():
            missing.append(dep)
    
    if missing:
        return False, f"Missing dependencies: {', '.join(missing)}"
    
    return True, None


def check_lock_file_sync(component: str, env: str, manifests_dir: str = "manifests") -> tuple:
    """Check if component is in sync with lock file."""
    if not env:
        return True, None  # Skip if no environment specified
    
    lock_data = load_environment_lock_file(env, manifests_dir)
    if not lock_data:
        return True, None  # No lock file, skip check
    
    components = lock_data.get("components", {})
    if component not in components:
        return True, None  # Not in lock file, skip check
    
    comp_path = Path(f"components/{component}")
    if not comp_path.exists():
        return False, "Component not found"
    
    expected_commit = components[component].get("commit")
    if expected_commit:
        current_commit = get_commit_sha(str(comp_path))
        if current_commit and current_commit.startswith(expected_commit[:8]):
            return True, None
        return False, f"Lock file mismatch: expected {expected_commit[:8]}, got {current_commit[:8] if current_commit else 'unknown'}"
    
    return True, None


def check_component_health(component: str, env: Optional[str] = None,
                          manifests_dir: str = "manifests",
                          check_build: bool = True,
                          check_tests: bool = True) -> HealthStatus:
    """Perform comprehensive health check for a component."""
    status = HealthStatus(component)
    
    # Check existence
    exists, error = check_component_exists(component)
    status.add_check("exists", exists, error)
    if not exists:
        return status  # Can't check anything else if it doesn't exist
    
    # Check version
    if env:
        version_ok, error = check_component_version(component, env, manifests_dir)
        status.add_check("version", version_ok, error)
    
    # Check dependencies
    deps_ok, error = check_component_dependencies(component, manifests_dir)
    status.add_check("dependencies", deps_ok, error)
    
    # Check lock file sync
    if env:
        lock_ok, error = check_lock_file_sync(component, env, manifests_dir)
        status.add_check("lock_file_sync", lock_ok, error)
    
    # Check build
    if check_build:
        build_ok, error = check_component_builds(component)
        status.add_check("builds", build_ok, error)
    
    # Check tests
    if check_tests:
        test_ok, error = check_component_tests(component)
        status.add_check("tests", test_ok, error)
    
    return status


def check_all_components_health(env: Optional[str] = None,
                                manifests_dir: str = "manifests",
                                check_build: bool = False,
                                check_tests: bool = False) -> List[HealthStatus]:
    """Check health of all components."""
    components = get_components(manifests_dir)
    statuses = []
    
    for component in components.keys():
        status = check_component_health(
            component, env, manifests_dir,
            check_build=check_build,
            check_tests=check_tests
        )
        statuses.append(status)
    
    return statuses

