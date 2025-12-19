"""Lock file utilities for reproducible builds."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from meta.utils.logger import log, error, success
from meta.utils.manifest import get_components
from meta.utils.git import get_commit_sha, get_commit_sha_for_ref, git_available


def generate_lock_file(manifests_dir: str = "manifests", lock_file: str = "manifests/components.lock.yaml") -> bool:
    """Generate a lock file with exact commit SHAs for all components."""
    if not git_available():
        error("Git is not available - cannot generate lock file")
        return False
    
    log("Generating lock file...")
    components = get_components(manifests_dir)
    
    locked_components = {}
    
    for name, comp in components.items():
        repo_url = comp.get("repo", "")
        version = comp.get("version", "latest")
        
        if not repo_url:
            error(f"No repository URL for component {name}, skipping")
            continue
        
        # Try to get commit SHA for the version/tag
        commit_sha = None
        if version and version != "latest":
            commit_sha = get_commit_sha_for_ref(repo_url, version)
            if not commit_sha:
                # Try as branch name
                commit_sha = get_commit_sha_for_ref(repo_url, f"refs/heads/{version}")
            if not commit_sha:
                # Try as tag
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
        }
        
        log(f"  {name}: {version} -> {commit_sha[:8]}")
    
    # Write lock file
    lock_data = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "components": locked_components
    }
    
    lock_path = Path(lock_file)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(lock_path, 'w') as f:
        yaml.dump(lock_data, f, default_flow_style=False, sort_keys=False)
    
    success(f"Lock file generated: {lock_file}")
    return True


def load_lock_file(lock_file: str = "manifests/components.lock.yaml") -> Optional[Dict[str, Any]]:
    """Load and parse a lock file."""
    lock_path = Path(lock_file)
    if not lock_path.exists():
        return None
    
    try:
        with open(lock_path, 'r') as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        error(f"Failed to parse lock file {lock_file}: {e}")
        return None


def get_locked_components(lock_file: str = "manifests/components.lock.yaml") -> Dict[str, Any]:
    """Get locked components from lock file."""
    lock_data = load_lock_file(lock_file)
    if not lock_data:
        return {}
    return lock_data.get("components", {})


def validate_lock_file(manifests_dir: str = "manifests", lock_file: str = "manifests/components.lock.yaml") -> bool:
    """Validate that lock file matches current components manifest."""
    components = get_components(manifests_dir)
    locked_components = get_locked_components(lock_file)
    
    if not locked_components:
        error("Lock file is empty or missing")
        return False
    
    all_valid = True
    
    # Check that all components in manifest are in lock file
    for name in components.keys():
        if name not in locked_components:
            error(f"Component {name} in manifest but not in lock file")
            all_valid = False
    
    # Check that all components in lock file are in manifest
    for name in locked_components.keys():
        if name not in components:
            error(f"Component {name} in lock file but not in manifest")
            all_valid = False
    
    # Check that versions match
    for name, comp in components.items():
        if name in locked_components:
            locked = locked_components[name]
            if comp.get("version") != locked.get("version"):
                error(f"Version mismatch for {name}: manifest={comp.get('version')}, lock={locked.get('version')}")
                all_valid = False
    
    return all_valid


