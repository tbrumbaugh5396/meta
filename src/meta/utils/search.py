"""Enhanced component search utilities."""

import re
from typing import Dict, Any, List, Optional
from meta.utils.logger import log
from meta.utils.manifest import get_components
from meta.utils.git import get_current_version
from meta.utils.health import check_component_health


def search_components(
    query: str,
    search_type: str = "name",
    manifests_dir: str = "manifests"
) -> List[Dict[str, Any]]:
    """Search components with enhanced filtering."""
    components = get_components(manifests_dir)
    results = []
    
    query_lower = query.lower()
    
    for name, comp in components.items():
        match = False
        match_data = {
            "name": name,
            "type": comp.get("type", "unknown"),
            "version": comp.get("version", "unknown"),
            "repo": comp.get("repo", ""),
            "matches": []
        }
        
        if search_type == "name" or search_type == "all":
            if query_lower in name.lower():
                match = True
                match_data["matches"].append("name")
        
        if search_type == "type" or search_type == "all":
            comp_type = comp.get("type", "").lower()
            if query_lower in comp_type:
                match = True
                match_data["matches"].append("type")
        
        if search_type == "repo" or search_type == "all":
            repo = comp.get("repo", "").lower()
            if query_lower in repo:
                match = True
                match_data["matches"].append("repo")
        
        if search_type == "tag" or search_type == "all":
            tags = comp.get("tags", [])
            for tag in tags:
                if query_lower in tag.lower():
                    match = True
                    match_data["matches"].append(f"tag:{tag}")
        
        if match:
            # Add current version
            try:
                current_version = get_current_version(f"components/{name}")
                match_data["current_version"] = current_version or "not checked out"
            except:
                match_data["current_version"] = "unknown"
            
            results.append(match_data)
    
    return results


def search_by_dependency(
    dependency: str,
    manifests_dir: str = "manifests"
) -> List[str]:
    """Find components that depend on a given component."""
    components = get_components(manifests_dir)
    dependents = []
    
    for name, comp in components.items():
        deps = comp.get("dependencies", [])
        if dependency in deps:
            dependents.append(name)
    
    return dependents


def search_by_version(
    version_pattern: str,
    manifests_dir: str = "manifests"
) -> List[Dict[str, Any]]:
    """Search components by version pattern."""
    components = get_components(manifests_dir)
    results = []
    
    try:
        pattern = re.compile(version_pattern)
    except re.error:
        return results
    
    for name, comp in components.items():
        version = comp.get("version", "")
        if pattern.search(version):
            results.append({
                "name": name,
                "version": version,
                "type": comp.get("type", "unknown")
            })
    
    return results


