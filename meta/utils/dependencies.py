"""Dependency resolution and validation utilities."""

from typing import Dict, Any, List, Set, Optional, Tuple
from meta.utils.logger import log, error
from meta.utils.manifest import get_components


def get_component_dependencies(component_name: str, components: Dict[str, Any]) -> List[str]:
    """Get direct dependencies for a component."""
    comp = components.get(component_name)
    if not comp:
        return []
    return comp.get("depends_on", [])


def resolve_transitive_dependencies(component_name: str, components: Dict[str, Any], visited: Optional[Set[str]] = None) -> List[str]:
    """Resolve all transitive dependencies for a component (topological order)."""
    if visited is None:
        visited = set()
    
    if component_name in visited:
        return []  # Already processed
    
    visited.add(component_name)
    
    direct_deps = get_component_dependencies(component_name, components)
    all_deps = list(direct_deps)
    
    # Recursively get dependencies of dependencies
    for dep in direct_deps:
        transitive = resolve_transitive_dependencies(dep, components, visited)
        # Add transitive deps that aren't already in the list
        for trans_dep in transitive:
            if trans_dep not in all_deps:
                all_deps.append(trans_dep)
    
    return all_deps


def validate_dependencies(manifests_dir: str = "manifests") -> Tuple[bool, List[str]]:
    """Validate that all component dependencies exist and there are no cycles."""
    components = get_components(manifests_dir)
    errors = []
    
    # Check that all dependencies exist
    for name, comp in components.items():
        deps = comp.get("depends_on", [])
        for dep in deps:
            if dep not in components:
                error_msg = f"Component '{name}' depends on '{dep}' which does not exist"
                error(error_msg)
                errors.append(error_msg)
    
    # Check for cycles using DFS
    visited = set()
    rec_stack = set()
    cycle_nodes = []
    
    def has_cycle(node: str) -> bool:
        visited.add(node)
        rec_stack.add(node)
        
        deps = get_component_dependencies(node, components)
        for dep in deps:
            if dep not in visited:
                if has_cycle(dep):
                    cycle_nodes.append(node)
                    return True
            elif dep in rec_stack:
                cycle_nodes.append(node)
                cycle_nodes.append(dep)
                return True
        
        rec_stack.remove(node)
        return False
    
    for comp_name in components.keys():
        if comp_name not in visited:
            if has_cycle(comp_name):
                error_msg = f"Circular dependency detected: {' -> '.join(cycle_nodes)}"
                error(error_msg)
                errors.append(error_msg)
                break
    
    return len(errors) == 0, errors


def get_dependency_order(components: Dict[str, Any]) -> List[str]:
    """Get components in dependency order (topological sort)."""
    # Build dependency graph
    graph = {}
    in_degree = {}
    
    for name in components.keys():
        graph[name] = get_component_dependencies(name, components)
        in_degree[name] = 0
    
    # Calculate in-degrees
    for name, deps in graph.items():
        for dep in deps:
            if dep in in_degree:
                in_degree[dep] = in_degree.get(dep, 0) + 1
    
    # Topological sort using Kahn's algorithm
    queue = [name for name, degree in in_degree.items() if degree == 0]
    result = []
    
    while queue:
        node = queue.pop(0)
        result.append(node)
        
        for dep in graph[node]:
            if dep in in_degree:
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)
    
    # Check for cycles (if result doesn't include all nodes)
    if len(result) != len(components):
        remaining = set(components.keys()) - set(result)
        error(f"Circular dependencies detected involving: {remaining}")
        # Return what we have plus remaining (unsorted)
        result.extend(remaining)
    
    return result

