"""Component comparison utilities."""

from typing import Dict, Any, List, Optional
from pathlib import Path
from meta.utils.logger import log, error
from meta.utils.manifest import get_components, get_environment_config
from meta.utils.git import get_current_version, get_commit_sha
from meta.utils.lock import get_locked_components
from meta.utils.environment_locks import load_environment_lock_file
from meta.utils.dependencies import resolve_transitive_dependencies


def compare_components(component1: str, component2: str,
                      manifests_dir: str = "manifests") -> Dict[str, Any]:
    """Compare two components."""
    components = get_components(manifests_dir)
    
    if component1 not in components:
        error(f"Component {component1} not found")
        return {}
    
    if component2 not in components:
        error(f"Component {component2} not found")
        return {}
    
    comp1_data = components[component1]
    comp2_data = components[component2]
    
    # Get dependencies
    deps = resolve_transitive_dependencies(components)
    comp1_deps = list(deps.get(component1, set()))
    comp2_deps = list(deps.get(component2, set()))
    
    # Get current versions
    comp1_path = Path(f"components/{component1}")
    comp2_path = Path(f"components/{component2}")
    
    comp1_current = get_current_version(str(comp1_path)) if comp1_path.exists() else None
    comp2_current = get_current_version(str(comp2_path)) if comp2_path.exists() else None
    
    return {
        "component1": {
            "name": component1,
            "version": comp1_data.get("version"),
            "current_version": comp1_current,
            "type": comp1_data.get("type"),
            "dependencies": comp1_deps,
            "repo": comp1_data.get("repo"),
        },
        "component2": {
            "name": component2,
            "version": comp2_data.get("version"),
            "current_version": comp2_current,
            "type": comp2_data.get("type"),
            "dependencies": comp2_deps,
            "repo": comp2_data.get("repo"),
        },
        "differences": {
            "version": comp1_data.get("version") != comp2_data.get("version"),
            "type": comp1_data.get("type") != comp2_data.get("type"),
            "dependencies": set(comp1_deps) != set(comp2_deps),
        }
    }


def compare_environments(env1: str, env2: str,
                        manifests_dir: str = "manifests"):
    """Compare two environments."""
    config1 = get_environment_config(env1, manifests_dir)
    config2 = get_environment_config(env2, manifests_dir)
    
    components = get_components(manifests_dir)
    
    differences = []
    for comp_name in components.keys():
        comp1_version = config1.get("components", {}).get(comp_name, {}).get("version")
        comp2_version = config2.get("components", {}).get(comp_name, {}).get("version")
        
        if comp1_version != comp2_version:
            differences.append({
                "component": comp_name,
                "env1_version": comp1_version,
                "env2_version": comp2_version
            })
    
    return {
        "env1": env1,
        "env2": env2,
        "differences": differences,
        "total_differences": len(differences)
    }

