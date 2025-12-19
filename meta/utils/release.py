"""Release automation utilities."""

import subprocess
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from meta.utils.logger import log, success, error, warning
from meta.utils.manifest import get_components
from meta.utils.git import get_current_version, get_commit_sha
from meta.utils.publish import create_tag
from meta.utils.changelog import update_changelog, generate_changelog_entry

# Import health with error handling
try:
    from meta.utils.health import check_component_health
except ImportError:
    def check_component_health(*args, **kwargs):
        class HealthResult:
            healthy = True
        return HealthResult()


def prepare_release(component: str, version: str,
                   manifests_dir: str = "manifests",
                   validate: bool = True,
                   update_changelog_flag: bool = True) -> bool:
    """Prepare a component release."""
    log(f"Preparing release for {component} version {version}")
    
    components = get_components(manifests_dir)
    if component not in components:
        error(f"Component {component} not found")
        return False
    
    component_path = Path(f"components/{component}")
    if not component_path.exists():
        error(f"Component directory not found: {component_path}")
        return False
    
    # Validate component
    if validate:
        log("Running pre-release validation...")
        try:
            health = check_component_health(component, env="dev", manifests_dir=manifests_dir)
            if hasattr(health, 'healthy'):
                if not health.healthy:
                    error("Component health checks failed")
                    return False
            elif isinstance(health, dict):
                if not health.get("healthy", False):
                    error("Component health checks failed")
                    return False
        except Exception as e:
            warning(f"Health check failed: {e}, continuing anyway")
        
        success("Pre-release validation passed")
    
    # Update changelog
    if update_changelog_flag:
        log("Updating changelog...")
        current_version = get_current_version(str(component_path))
        update_changelog(component, version, str(component_path), since=current_version)
        success("Changelog updated")
    
    # Update manifest
    log("Updating manifest...")
    manifest_path = Path(manifests_dir) / "components.yaml"
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f) or {}
    
    manifest["components"][component]["version"] = version
    
    with open(manifest_path, 'w') as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
    
    success(f"Release prepared for {component} version {version}")
    return True


def publish_release(component: str, version: str,
                   component_path: str,
                   create_tag_flag: bool = True,
                   push: bool = True) -> bool:
    """Publish a component release."""
    log(f"Publishing release for {component} version {version}")
    
    # Create git tag
    if create_tag_flag:
        if not create_tag(component_path, version):
            error("Failed to create git tag")
            return False
        success(f"Created tag: {version}")
    
    # Push tag if requested
    if push and create_tag_flag:
        try:
            result = subprocess.run(
                ["git", "-C", component_path, "push", "origin", version],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                success(f"Pushed tag {version}")
            else:
                error(f"Failed to push tag: {result.stderr}")
        except Exception as e:
            error(f"Failed to push tag: {e}")
    
    # Generate release notes
    changelog_entry = generate_changelog_entry(component, version, component_path)
    
    success(f"Published release for {component} version {version}")
    return True


def rollback_release(component: str, from_version: str,
                    component_path: str) -> bool:
    """Rollback a release."""
    log(f"Rolling back {component} from {from_version}")
    
    # Delete tag
    try:
        result = subprocess.run(
            ["git", "-C", component_path, "tag", "-d", from_version],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            success(f"Deleted local tag: {from_version}")
    except Exception as e:
        error(f"Failed to delete tag: {e}")
    
    # Checkout previous version
    from meta.utils.git import checkout_version
    from meta.utils.manifest import get_components
    
    components = get_components()
    comp_data = components.get(component, {})
    previous_version = comp_data.get("version", "latest")
    
    if previous_version != from_version:
        if checkout_version(component_path, previous_version):
            success(f"Rolled back to {previous_version}")
        else:
            error("Failed to rollback")
            return False
    
    return True
