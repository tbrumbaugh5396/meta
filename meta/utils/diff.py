"""Lock file diff utilities."""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, error
from meta.utils.lock import load_lock_file
from meta.utils.environment_locks import load_environment_lock_file


def diff_lock_files(lock_file1: str, lock_file2: str):
    """Compare two lock files."""
    lock1 = load_lock_file(lock_file1)
    lock2 = load_lock_file(lock_file2)
    
    if not lock1 or not lock2:
        return {}
    
    comp1 = lock1.get("components", {})
    comp2 = lock2.get("components", {})
    
    all_components = set(comp1.keys()) | set(comp2.keys())
    
    differences = {
        "only_in_file1": [],
        "only_in_file2": [],
        "version_differences": [],
        "commit_differences": []
    }
    
    for comp_name in all_components:
        if comp_name not in comp1:
            differences["only_in_file2"].append(comp_name)
            continue
        
        if comp_name not in comp2:
            differences["only_in_file1"].append(comp_name)
            continue
        
        comp1_data = comp1[comp_name]
        comp2_data = comp2[comp_name]
        
        if comp1_data.get("version") != comp2_data.get("version"):
            differences["version_differences"].append({
                "component": comp_name,
                "file1_version": comp1_data.get("version"),
                "file2_version": comp2_data.get("version")
            })
        
        if comp1_data.get("commit") != comp2_data.get("commit"):
            differences["commit_differences"].append({
                "component": comp_name,
                "file1_commit": comp1_data.get("commit", "")[:8] if comp1_data.get("commit") else None,
                "file2_commit": comp2_data.get("commit", "")[:8] if comp2_data.get("commit") else None
            })
    
    return differences


def diff_environments(env1: str, env2: str,
                     manifests_dir: str = "manifests"):
    """Compare lock files for two environments."""
    from meta.utils.environment_locks import get_env_lock_file_path
    
    lock_file1 = get_env_lock_file_path(env1, manifests_dir)
    lock_file2 = get_env_lock_file_path(env2, manifests_dir)
    
    if not lock_file1.exists():
        error(f"Lock file not found for {env1}: {lock_file1}")
        return {}
    
    if not lock_file2.exists():
        error(f"Lock file not found for {env2}: {lock_file2}")
        return {}
    
    return diff_lock_files(str(lock_file1), str(lock_file2))

