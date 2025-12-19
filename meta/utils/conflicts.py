"""Dependency conflict detection and resolution."""

from typing import Dict, Any, List, Tuple, Optional
from meta.utils.manifest import get_components
from meta.utils.dependencies import get_component_dependencies, resolve_transitive_dependencies
from meta.utils.semver import satisfies_range, compare_versions, VersionComparison
from meta.utils.logger import log, error, warning


class Conflict:
    """Represents a dependency conflict."""
    def __init__(self, component: str, dependency: str, required_range: str, 
                 conflicting_versions: List[Tuple[str, str]]):
        self.component = component
        self.dependency = dependency
        self.required_range = required_range
        self.conflicting_versions = conflicting_versions  # List of (component, version)
    
    def __str__(self):
        versions_str = ", ".join([f"{comp}@{ver}" for comp, ver in self.conflicting_versions])
        return f"{self.component} requires {self.dependency} {self.required_range}, but found: {versions_str}"


def detect_conflicts(manifests_dir: str = "manifests") -> List[Conflict]:
    """Detect dependency conflicts in component dependencies."""
    components = get_components(manifests_dir)
    conflicts = []
    
    # Build dependency map: dependency_name -> [(component, version_range), ...]
    dependency_map: Dict[str, List[Tuple[str, str]]] = {}
    
    for comp_name, comp_data in components.items():
        deps = comp_data.get("depends_on", [])
        for dep in deps:
            # Check if dependency has version range specified
            if isinstance(dep, dict):
                dep_name = dep.get("name")
                dep_range = dep.get("version", "*")
            elif ":" in dep:
                # Format: "component-name:version-range"
                parts = dep.split(":", 1)
                dep_name = parts[0]
                dep_range = parts[1] if len(parts) > 1 else "*"
            else:
                dep_name = dep
                dep_range = "*"
            
            if dep_name not in dependency_map:
                dependency_map[dep_name] = []
            dependency_map[dep_name].append((comp_name, dep_range))
    
    # Check for conflicts
    for dep_name, requirements in dependency_map.items():
        if len(requirements) < 2:
            continue  # No conflict possible with single requirement
        
        # Check if all requirements are compatible
        # For now, we'll flag if ranges don't overlap
        # This is simplified - a full implementation would check actual version compatibility
        
        # If any requirement is exact version, check others satisfy it
        exact_versions = [r for _, r in requirements if r != "*" and not any(op in r for op in ["^", "~", ">", "<", "="])]
        
        if exact_versions:
            # Check if all exact versions are the same
            if len(set(exact_versions)) > 1:
                conflicts.append(Conflict(
                    component="multiple",
                    dependency=dep_name,
                    required_range="multiple",
                    conflicting_versions=requirements
                ))
        else:
            # Check range compatibility (simplified)
            # In a full implementation, we'd check if ranges overlap
            ranges = [r for _, r in requirements if r != "*"]
            if len(set(ranges)) > 1:
                # Potential conflict - ranges differ
                # For now, we'll flag it but not fail
                pass
    
    return conflicts


def resolve_conflict(conflict: Conflict, strategy: str = "latest") -> Optional[str]:
    """
    Resolve a conflict using a strategy.
    Strategies: "latest", "conservative", "first", "highest"
    """
    if not conflict.conflicting_versions:
        return None
    
    if strategy == "latest":
        # Use the latest version from all requirements
        # This is simplified - would need to fetch available versions
        versions = [ver for _, ver in conflict.conflicting_versions if ver != "*"]
        if versions:
            # Sort and return latest
            sorted_versions = sorted(versions, key=lambda v: parse_version_for_sort(v), reverse=True)
            return sorted_versions[0]
    
    elif strategy == "conservative":
        # Use the lowest version that satisfies all requirements
        # This is simplified
        versions = [ver for _, ver in conflict.conflicting_versions if ver != "*"]
        if versions:
            sorted_versions = sorted(versions, key=lambda v: parse_version_for_sort(v))
            return sorted_versions[0]
    
    elif strategy == "first":
        # Use the first requirement's version
        return conflict.conflicting_versions[0][1]
    
    elif strategy == "highest":
        # Use the highest version
        versions = [ver for _, ver in conflict.conflicting_versions if ver != "*"]
        if versions:
            sorted_versions = sorted(versions, key=lambda v: parse_version_for_sort(v), reverse=True)
            return sorted_versions[0]
    
    return None


def parse_version_for_sort(version_str: str) -> Tuple[int, int, int]:
    """Parse version for sorting (simplified, ignores prerelease)."""
    from meta.utils.semver import parse_version
    parsed = parse_version(version_str)
    if parsed:
        major, minor, patch, _ = parsed
        return (major, minor, patch)
    return (0, 0, 0)


def recommend_updates(manifests_dir: str = "manifests") -> Dict[str, List[Dict[str, Any]]]:
    """Recommend dependency updates based on available versions."""
    components = get_components(manifests_dir)
    recommendations = {}
    
    for comp_name, comp_data in components.items():
        deps = comp_data.get("depends_on", [])
        comp_recommendations = []
        
        for dep in deps:
            if isinstance(dep, dict):
                dep_name = dep.get("name")
                current_range = dep.get("version", "*")
            elif ":" in dep:
                parts = dep.split(":", 1)
                dep_name = parts[0]
                current_range = parts[1] if len(parts) > 1 else "*"
            else:
                dep_name = dep
                current_range = "*"
            
            # In a full implementation, we'd fetch available versions from the dependency
            # For now, we'll just note that updates might be available
            comp_recommendations.append({
                "dependency": dep_name,
                "current": current_range,
                "recommendation": "Check for updates",
                "reason": "Version check not implemented"
            })
        
        if comp_recommendations:
            recommendations[comp_name] = comp_recommendations
    
    return recommendations


