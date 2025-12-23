"""Component discovery utilities."""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error
from meta.utils.manifest import get_components


def detect_component_type(path: Path) -> Optional[str]:
    """Detect component type from directory structure."""
    # Check for Bazel
    if (path / "BUILD.bazel").exists() or (path / "BUILD").exists():
        return "bazel"
    
    # Check for Python
    if (path / "setup.py").exists() or (path / "pyproject.toml").exists():
        return "python"
    
    # Check for npm
    if (path / "package.json").exists():
        return "npm"
    
    # Check for Go
    if (path / "go.mod").exists():
        return "go"
    
    # Check for Rust
    if (path / "Cargo.toml").exists():
        return "rust"
    
    return None


def discover_components(base_path: str, recursive: bool = True) -> List[Dict[str, Any]]:
    """Discover components in a directory."""
    base = Path(base_path)
    if not base.exists():
        error(f"Path does not exist: {base_path}")
        return []
    
    components = []
    
    if recursive:
        # Recursive search
        for item in base.rglob("*"):
            if item.is_dir():
                comp_type = detect_component_type(item)
                if comp_type:
                    # Check if it's not already a subdirectory of another component
                    is_subdir = False
                    for existing in components:
                        existing_path = Path(existing["path"])
                        try:
                            item.relative_to(existing_path)
                            is_subdir = True
                            break
                        except ValueError:
                            pass
                    
                    if not is_subdir:
                        components.append({
                            "name": item.name,
                            "path": str(item),
                            "type": comp_type
                        })
    else:
        # Non-recursive
        for item in base.iterdir():
            if item.is_dir():
                comp_type = detect_component_type(item)
                if comp_type:
                    components.append({
                        "name": item.name,
                        "path": str(item),
                        "type": comp_type
                    })
    
    return components


def validate_component_structure(path: Path):
    """Validate component structure."""
    errors = []
    
    if not path.exists():
        errors.append("Component directory does not exist")
        return False, errors
    
    comp_type = detect_component_type(path)
    if not comp_type:
        errors.append("Could not detect component type")
        return False, errors
    
    # Type-specific validation
    if comp_type == "bazel":
        if not (path / "BUILD.bazel").exists() and not (path / "BUILD").exists():
            errors.append("Missing BUILD.bazel or BUILD file")
    elif comp_type == "python":
        if not (path / "setup.py").exists() and not (path / "pyproject.toml").exists():
            errors.append("Missing setup.py or pyproject.toml")
    elif comp_type == "npm":
        if not (path / "package.json").exists():
            errors.append("Missing package.json")
    
    # Common validations
    if not (path / "README.md").exists():
        errors.append("Missing README.md (recommended)")
    
    return len(errors) == 0, errors


def generate_manifest_entry(component: Dict[str, Any], repo_url: Optional[str] = None) -> Dict[str, Any]:
    """Generate manifest entry for discovered component."""
    entry = {
        "type": component["type"],
        "version": "0.1.0",  # Default version
    }
    
    if repo_url:
        entry["repo"] = repo_url
    else:
        # Try to detect git remote
        import subprocess
        try:
            result = subprocess.run(
                ["git", "-C", component["path"], "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                entry["repo"] = result.stdout.strip()
        except:
            pass
    
    if component["type"] == "bazel":
        entry["build_target"] = "//..."
    
    return entry

