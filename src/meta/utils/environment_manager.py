"""Environment management utilities."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from meta.utils.logger import log, error, success
from meta.utils.manifest import find_meta_repo_root, get_components, get_environments


def get_environments_file_path(manifests_dir: str = "manifests") -> Path:
    """Get the path to environments.yaml file."""
    root = find_meta_repo_root()
    if root:
        return root / manifests_dir / "environments.yaml"
    else:
        return Path(manifests_dir) / "environments.yaml"


def load_environments_file(manifests_dir: str = "manifests") -> Dict[str, Any]:
    """Load environments.yaml file."""
    env_file = get_environments_file_path(manifests_dir)
    if not env_file.exists():
        return {"environments": {}}
    
    with open(env_file, 'r') as f:
        try:
            return yaml.safe_load(f) or {"environments": {}}
        except yaml.YAMLError as e:
            error(f"Failed to parse environments.yaml: {e}")
            raise


def save_environments_file(data: Dict[str, Any], manifests_dir: str = "manifests") -> bool:
    """Save environments.yaml file."""
    env_file = get_environments_file_path(manifests_dir)
    
    # Ensure directory exists
    env_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(env_file, 'w') as f:
        try:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, indent=2)
            return True
        except Exception as e:
            error(f"Failed to save environments.yaml: {e}")
            return False


def get_default_environments(manifests_dir: str = "manifests") -> Dict[str, Any]:
    """Get default environments (dev, staging, prod) with all components."""
    components = get_components(manifests_dir)
    component_names = list(components.keys())
    
    default_envs = {}
    for env_name in ["dev", "staging", "prod"]:
        default_envs[env_name] = {}
        for comp_name in component_names:
            default_envs[env_name][comp_name] = env_name
    
    return default_envs


def add_environment(
    env_name: str,
    manifests_dir: str = "manifests",
    from_env: Optional[str] = None,
    component_versions: Optional[Dict[str, str]] = None
) -> bool:
    """Add a new environment."""
    data = load_environments_file(manifests_dir)
    environments = data.get("environments", {})
    
    if env_name in environments:
        error(f"Environment '{env_name}' already exists")
        return False
    
    components = get_components(manifests_dir)
    component_names = list(components.keys())
    
    # Build new environment
    new_env = {}
    
    if from_env:
        # Copy from existing environment
        if from_env not in environments:
            error(f"Source environment '{from_env}' does not exist")
            return False
        source_env = environments[from_env]
        for comp_name in component_names:
            # Use source version if component exists in source, otherwise use env_name
            new_env[comp_name] = source_env.get(comp_name, env_name)
    else:
        # Default: use env_name as version for all components
        for comp_name in component_names:
            new_env[comp_name] = env_name
    
    # Override with explicit component versions if provided
    if component_versions:
        for comp_name, version in component_versions.items():
            if comp_name not in component_names:
                error(f"Component '{comp_name}' not found in components.yaml")
                return False
            new_env[comp_name] = version
    
    environments[env_name] = new_env
    data["environments"] = environments
    
    if save_environments_file(data, manifests_dir):
        success(f"Added environment '{env_name}'")
        return True
    return False


def delete_environment(env_name: str, manifests_dir: str = "manifests") -> bool:
    """Delete an environment."""
    data = load_environments_file(manifests_dir)
    environments = data.get("environments", {})
    
    if env_name not in environments:
        error(f"Environment '{env_name}' does not exist")
        return False
    
    # Prevent deletion of standard environments
    if env_name in ["dev", "staging", "prod"]:
        error(f"Cannot delete standard environment '{env_name}'. Use 'reset' to restore defaults.")
        return False
    
    del environments[env_name]
    data["environments"] = environments
    
    if save_environments_file(data, manifests_dir):
        success(f"Deleted environment '{env_name}'")
        return True
    return False


def reset_environments(manifests_dir: str = "manifests") -> bool:
    """Reset environments to defaults (dev, staging, prod)."""
    default_envs = get_default_environments(manifests_dir)
    data = {"environments": default_envs}
    
    if save_environments_file(data, manifests_dir):
        success("Reset environments to defaults (dev, staging, prod)")
        return True
    return False


def edit_environment(
    env_name: str,
    manifests_dir: str = "manifests",
    component_versions: Optional[Dict[str, str]] = None,
    set_all: Optional[str] = None
) -> bool:
    """Edit an environment (set component versions)."""
    data = load_environments_file(manifests_dir)
    environments = data.get("environments", {})
    
    if env_name not in environments:
        error(f"Environment '{env_name}' does not exist")
        return False
    
    components = get_components(manifests_dir)
    component_names = list(components.keys())
    
    # If set_all is provided, set all components to that version
    if set_all:
        environments[env_name] = {}
        for comp_name in component_names:
            environments[env_name][comp_name] = set_all
    elif component_versions:
        # Update specific components
        for comp_name, version in component_versions.items():
            if comp_name not in component_names:
                error(f"Component '{comp_name}' not found in components.yaml")
                return False
            environments[env_name][comp_name] = version
    
    data["environments"] = environments
    
    if save_environments_file(data, manifests_dir):
        success(f"Updated environment '{env_name}'")
        return True
    return False


def list_environments(manifests_dir: str = "manifests") -> List[str]:
    """List all environments."""
    environments = get_environments(manifests_dir)
    return sorted(environments.keys())


def show_environment(env_name: str, manifests_dir: str = "manifests") -> Optional[Dict[str, str]]:
    """Show details of an environment."""
    environments = get_environments(manifests_dir)
    return environments.get(env_name)

