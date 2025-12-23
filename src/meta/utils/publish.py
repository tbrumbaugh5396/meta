"""Component publishing utilities."""

import subprocess
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from meta.utils.logger import log, success, error
from meta.utils.manifest import get_components
from meta.utils.git import get_current_version, get_commit_sha
from meta.utils.version import compare_versions, normalize_version


def bump_version(current_version: str, bump_type: str = "patch") -> str:
    """Bump version string."""
    normalized = normalize_version(current_version)
    parts = normalized.split('.')
    
    if len(parts) < 3:
        parts = parts + ['0'] * (3 - len(parts))
    
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    return f"v{major}.{minor}.{patch}"


def create_tag(repo_path: str, version: str, message: Optional[str] = None) -> bool:
    """Create git tag."""
    try:
        if message is None:
            message = f"Release {version}"
        
        result = subprocess.run(
            ["git", "-C", repo_path, "tag", "-a", version, "-m", message],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return result.returncode == 0
    except Exception as e:
        error(f"Failed to create tag: {e}")
        return False


def generate_changelog(component: str, version: str,
                      manifests_dir: str = "manifests") -> str:
    """Generate changelog entry."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d")
    
    changelog = f"""## [{version}] - {timestamp}

### Added
- Component updates

### Changed
- Version bump to {version}

### Notes
- Published via meta-repo CLI
"""
    return changelog


def publish_component(component: str, version: Optional[str] = None,
                     bump_type: str = "patch",
                     manifests_dir: str = "manifests",
                     create_tag_flag: bool = True,
                     update_manifest: bool = True) -> bool:
    """Publish a component."""
    log(f"Publishing component: {component}")
    
    components = get_components(manifests_dir)
    if component not in components:
        error(f"Component {component} not found")
        return False
    
    comp_data = components[component]
    comp_path = Path(f"components/{component}")
    
    if not comp_path.exists():
        error(f"Component directory not found: {comp_path}")
        return False
    
    # Determine version
    if version is None:
        current = comp_data.get("version", "v0.1.0")
        version = bump_version(current, bump_type)
    
    log(f"Publishing version: {version}")
    
    # Create tag
    if create_tag_flag:
        if not create_tag(str(comp_path), version):
            error("Failed to create git tag")
            return False
        success(f"Created tag: {version}")
    
    # Update manifest
    if update_manifest:
        manifest_path = Path(manifests_dir) / "components.yaml"
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f) or {}
        
        manifest["components"][component]["version"] = version
        
        with open(manifest_path, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
        
        success(f"Updated manifest: {component} -> {version}")
    
    # Generate changelog
    changelog = generate_changelog(component, version, manifests_dir)
    changelog_path = comp_path / "CHANGELOG.md"
    
    if changelog_path.exists():
        with open(changelog_path, 'r') as f:
            existing = f.read()
        with open(changelog_path, 'w') as f:
            f.write(changelog + "\n" + existing)
    else:
        with open(changelog_path, 'w') as f:
            f.write(f"# Changelog\n\n{changelog}")
    
    success(f"Published {component} version {version}")
    return True


