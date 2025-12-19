"""Component update utilities."""

import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from meta.utils.logger import log, success, error
from meta.utils.manifest import get_components
from meta.utils.git import get_current_version, get_commit_sha
from meta.utils.version import compare_versions


def get_latest_version(repo_url: str, current_version: Optional[str] = None) -> Optional[str]:
    """Get latest version tag from repository."""
    try:
        # Try to get latest tag
        result = subprocess.run(
            ["git", "ls-remote", "--tags", repo_url],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return None
        
        tags = []
        for line in result.stdout.splitlines():
            if "refs/tags/" in line:
                tag = line.split("refs/tags/")[-1].strip()
                # Filter out non-version tags
                if tag and not tag.endswith("^{}"):
                    tags.append(tag)
        
        if not tags:
            return None
        
        # Sort by version
        tags.sort(key=lambda x: compare_versions(x, x) if compare_versions else x, reverse=True)
        return tags[0] if tags else None
    except Exception as e:
        error(f"Failed to get latest version: {e}")
        return None


def check_component_updates(component: str, manifests_dir: str = "manifests") -> Optional[Dict[str, Any]]:
    """Check if component has updates available."""
    components = get_components(manifests_dir)
    
    if component not in components:
        return None
    
    comp_data = components[component]
    repo_url = comp_data.get("repo")
    current_version = comp_data.get("version", "latest")
    
    if not repo_url:
        return None
    
    # Get current local version
    comp_path = Path(f"components/{component}")
    local_version = None
    if comp_path.exists():
        local_version = get_current_version(str(comp_path))
    
    # Get latest version
    latest_version = get_latest_version(repo_url, current_version)
    
    if not latest_version:
        return None
    
    # Compare versions
    update_available = False
    if latest_version != current_version:
        if current_version != "latest":
            # Compare semantic versions
            if compare_versions(latest_version, current_version) > 0:
                update_available = True
        else:
            update_available = True
    
    return {
        "component": component,
        "current_version": current_version,
        "local_version": local_version,
        "latest_version": latest_version,
        "update_available": update_available,
        "repo_url": repo_url
    }


def check_all_updates(manifests_dir: str = "manifests") -> List[Dict[str, Any]]:
    """Check all components for updates."""
    components = get_components(manifests_dir)
    updates = []
    
    for component in components.keys():
        update_info = check_component_updates(component, manifests_dir)
        if update_info and update_info["update_available"]:
            updates.append(update_info)
    
    return updates


