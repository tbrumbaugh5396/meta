"""Component sync utilities."""

import subprocess
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error
from meta.utils.manifest import get_components, get_environment_config
from meta.utils.git import get_current_version, pull_latest, checkout_version


def sync_component(
    component: str,
    env: str = "dev",
    manifests_dir: str = "manifests"
) -> bool:
    """Sync component to desired version."""
    components = get_components(manifests_dir)
    
    if component not in components:
        error(f"Component {component} not found")
        return False
    
    comp = components[component]
    env_config = get_environment_config(env, manifests_dir)
    
    # Get desired version from environment or component default
    desired_version = env_config.get("components", {}).get(component, {}).get("version")
    if not desired_version:
        desired_version = comp.get("version")
    
    if not desired_version:
        error(f"No version specified for {component}")
        return False
    
    # Get current version
    current_version = get_current_version(f"components/{component}")
    
    if current_version == desired_version:
        log(f"{component} is already at desired version: {desired_version}")
        return True
    
    log(f"Syncing {component} from {current_version} to {desired_version}...")
    
    try:
        # Pull latest
        pull_latest(f"components/{component}")
        
        # Checkout desired version
        checkout_version(f"components/{component}", desired_version)
        
        success(f"Synced {component} to {desired_version}")
        return True
    except Exception as e:
        error(f"Failed to sync {component}: {e}")
        return False


def sync_all_components(
    env: str = "dev",
    manifests_dir: str = "manifests"
) -> Dict[str, bool]:
    """Sync all components to desired versions."""
    components = get_components(manifests_dir)
    results = {}
    
    for component in components.keys():
        results[component] = sync_component(component, env, manifests_dir)
    
    return results


def sync_environment(
    env: str,
    manifests_dir: str = "manifests"
) -> Dict[str, bool]:
    """Sync all components in an environment."""
    return sync_all_components(env, manifests_dir)


