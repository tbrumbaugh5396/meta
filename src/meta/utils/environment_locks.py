"""Environment-specific lock file management."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from meta.utils.logger import log, error, success
from meta.utils.manifest import get_components, get_environment_config, find_meta_repo_root
from meta.utils.lock import generate_lock_file, load_lock_file, validate_lock_file
from meta.utils.git import get_commit_sha_for_ref, git_available, get_commit_sha
from meta.utils.vendor import is_vendored_mode, get_vendor_info


def get_environment_lock_file_path(env: str, manifests_dir: str = "manifests") -> str:
    """Get the lock file path for a specific environment."""
    return f"{manifests_dir}/components.lock.{env}.yaml"


def generate_environment_lock_file(env: str, manifests_dir: str = "manifests") -> bool:
    """Generate a lock file for a specific environment.
    
    In vendored mode: stores semantic versions only
    In reference mode: stores commit SHAs
    """
    if is_vendored_mode(manifests_dir):
        return generate_vendored_environment_lock_file(env, manifests_dir)
    else:
        return generate_reference_environment_lock_file(env, manifests_dir)


def generate_vendored_environment_lock_file(env: str, manifests_dir: str = "manifests") -> bool:
    """Generate environment lock file for vendored mode."""
    log(f"Generating lock file for environment: {env} (vendored mode)")
    
    # Get environment-specific component versions
    env_config = get_environment_config(env, manifests_dir)
    components = get_components(manifests_dir)
    root = find_meta_repo_root()
    
    if not root:
        error("Could not find meta-repo root")
        return False
    
    lock_file = get_environment_lock_file_path(env, manifests_dir)
    locked_components = {}
    
    for name, comp in components.items():
        # Use environment-specific version if available, otherwise use default
        version = env_config.get(name, comp.get("version", "latest"))
        
        comp_dir = root / "components" / name
        vendor_info = get_vendor_info(comp_dir) if comp_dir.exists() else None
        
        if not vendor_info:
            error(f"Component {name} not vendored. Run: meta vendor import {name}")
            continue
        
        locked_components[name] = {
            "version": vendor_info.get("version"),  # Semantic version only
            "repo": comp.get("repo", ""),
            "type": comp.get("type", "unknown"),
            "build_target": comp.get("build_target"),
            "depends_on": comp.get("depends_on", []),
            "environment": env,
            "vendored_at": vendor_info.get("vendored_at"),
        }
        
        log(f"  {name}: {vendor_info.get('version')}")
    
    # Write lock file
    lock_data = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "environment": env,
        "mode": "vendored",
        "components": locked_components
    }
    
    lock_path = Path(lock_file)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(lock_path, 'w') as f:
        yaml.dump(lock_data, f, default_flow_style=False, sort_keys=False)
    
    success(f"Lock file generated for {env}: {lock_file}")
    return True


def generate_reference_environment_lock_file(env: str, manifests_dir: str = "manifests") -> bool:
    """Generate environment lock file for reference mode (existing implementation)."""
    if not git_available():
        error("Git is not available - cannot generate lock file")
        return False
    
    log(f"Generating lock file for environment: {env}")
    
    # Get environment-specific component versions
    env_config = get_environment_config(env, manifests_dir)
    components = get_components(manifests_dir)
    
    lock_file = get_environment_lock_file_path(env, manifests_dir)
    locked_components = {}
    
    for name, comp in components.items():
        repo_url = comp.get("repo", "")
        # Use environment-specific version if available, otherwise use default
        version = env_config.get(name, comp.get("version", "latest"))
        
        if not repo_url:
            error(f"No repository URL for component {name}, skipping")
            continue
        
        # Try to get commit SHA for the version/tag
        commit_sha = None
        if version and version != "latest":
            commit_sha = get_commit_sha_for_ref(repo_url, version)
            if not commit_sha:
                commit_sha = get_commit_sha_for_ref(repo_url, f"refs/heads/{version}")
            if not commit_sha:
                commit_sha = get_commit_sha_for_ref(repo_url, f"refs/tags/{version}")
        
        # If component is already checked out, get its current commit
        comp_dir = f"components/{name}"
        if Path(comp_dir).exists():
            current_sha = get_commit_sha(comp_dir)
            if current_sha:
                commit_sha = current_sha
        
        if not commit_sha:
            error(f"Could not determine commit SHA for {name}@{version}")
            continue
        
        locked_components[name] = {
            "version": version,
            "commit": commit_sha,
            "repo": repo_url,
            "type": comp.get("type", "unknown"),
            "build_target": comp.get("build_target"),
            "depends_on": comp.get("depends_on", []),
            "environment": env,
        }
        
        log(f"  {name}: {version} -> {commit_sha[:8]}")
    
    # Write lock file
    lock_data = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "environment": env,
        "mode": "reference",
        "components": locked_components
    }
    
    lock_path = Path(lock_file)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(lock_path, 'w') as f:
        yaml.dump(lock_data, f, default_flow_style=False, sort_keys=False)
    
    success(f"Lock file generated for {env}: {lock_file}")
    return True


def load_environment_lock_file(env: str, manifests_dir: str = "manifests") -> Optional[Dict[str, Any]]:
    """Load lock file for a specific environment."""
    lock_file = get_environment_lock_file_path(env, manifests_dir)
    return load_lock_file(lock_file)


def validate_environment_lock_file(env: str, manifests_dir: str = "manifests") -> bool:
    """Validate lock file for a specific environment."""
    lock_file = get_environment_lock_file_path(env, manifests_dir)
    return validate_lock_file(manifests_dir, lock_file)


def promote_lock_file(from_env: str, to_env: str, manifests_dir: str = "manifests") -> bool:
    """Promote lock file from one environment to another."""
    log(f"Promoting lock file from {from_env} to {to_env}")
    
    # Load source lock file
    source_lock = load_environment_lock_file(from_env, manifests_dir)
    if not source_lock:
        error(f"Source lock file for {from_env} not found")
        return False
    
    # Create target lock file with updated environment
    target_lock_file = get_environment_lock_file_path(to_env, manifests_dir)
    lock_data = source_lock.copy()
    lock_data["environment"] = to_env
    lock_data["promoted_from"] = from_env
    lock_data["promoted_at"] = datetime.utcnow().isoformat() + "Z"
    
    # Update component environment tags
    for comp_name, comp_data in lock_data.get("components", {}).items():
        comp_data["environment"] = to_env
    
    lock_path = Path(target_lock_file)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(lock_path, 'w') as f:
        yaml.dump(lock_data, f, default_flow_style=False, sort_keys=False)
    
    success(f"Lock file promoted from {from_env} to {to_env}")
    return True


def compare_lock_files(env1: str, env2: str, manifests_dir: str = "manifests") -> Dict[str, Any]:
    """Compare two environment lock files and return differences."""
    lock1 = load_environment_lock_file(env1, manifests_dir)
    lock2 = load_environment_lock_file(env2, manifests_dir)
    
    if not lock1 or not lock2:
        return {"error": "One or both lock files not found"}
    
    comp1 = lock1.get("components", {})
    comp2 = lock2.get("components", {})
    
    differences = {
        "only_in_env1": [],
        "only_in_env2": [],
        "version_differences": [],
        "commit_differences": []
    }
    
    all_components = set(comp1.keys()) | set(comp2.keys())
    
    for comp_name in all_components:
        if comp_name not in comp1:
            differences["only_in_env2"].append(comp_name)
        elif comp_name not in comp2:
            differences["only_in_env1"].append(comp_name)
        else:
            c1 = comp1[comp_name]
            c2 = comp2[comp_name]
            
            if c1.get("version") != c2.get("version"):
                differences["version_differences"].append({
                    "component": comp_name,
                    f"{env1}_version": c1.get("version"),
                    f"{env2}_version": c2.get("version")
                })
            
            if c1.get("commit") != c2.get("commit"):
                differences["commit_differences"].append({
                    "component": comp_name,
                    f"{env1}_commit": c1.get("commit", "")[:8],
                    f"{env2}_commit": c2.get("commit", "")[:8]
                })
    
    return differences


