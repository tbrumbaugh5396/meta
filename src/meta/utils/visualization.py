"""Dependency visualization utilities."""

from typing import Dict, Any, List, Set, Optional
from meta.utils.manifest import get_components
from meta.utils.dependencies import resolve_transitive_dependencies


def generate_dot_graph(components: Optional[Dict[str, Any]] = None,
                      manifests_dir: str = "manifests") -> str:
    """Generate Graphviz DOT format graph."""
    if components is None:
        components = get_components(manifests_dir)
    
    # Build dependency graph directly from components
    deps = {}
    for comp_name in components.keys():
        deps[comp_name] = components[comp_name].get("depends_on", [])
    
    lines = ["digraph dependencies {"]
    lines.append("  rankdir=LR;")
    lines.append("  node [shape=box];")
    
    # Add nodes
    for comp_name in components.keys():
        lines.append(f'  "{comp_name}";')
    
    # Add edges
    for comp_name, comp_data in components.items():
        depends_on = comp_data.get("depends_on", [])
        for dep in depends_on:
            lines.append(f'  "{comp_name}" -> "{dep}";')
    
    lines.append("}")
    return "\n".join(lines)


def generate_mermaid_graph(components: Optional[Dict[str, Any]] = None,
                          manifests_dir: str = "manifests") -> str:
    """Generate Mermaid format graph."""
    if components is None:
        components = get_components(manifests_dir)
    
    # Build dependency graph directly from components
    deps = {}
    for comp_name in components.keys():
        deps[comp_name] = components[comp_name].get("depends_on", [])
    
    lines = ["graph TD"]
    
    # Add edges
    for comp_name, comp_data in components.items():
        depends_on = comp_data.get("depends_on", [])
        for dep in depends_on:
            lines.append(f'    {comp_name} --> {dep}')
    
    return "\n".join(lines)


def generate_text_tree(component: str,
                       components: Optional[Dict[str, Any]] = None,
                       manifests_dir: str = "manifests",
                       max_depth: int = 10) -> str:
    """Generate text tree representation."""
    if components is None:
        components = get_components(manifests_dir)
    
    if component not in components:
        return f"Component {component} not found"
    
    # Build dependency map directly from components
    deps_map = {}
    for comp_name, comp_data in components.items():
        deps_map[comp_name] = comp_data.get("depends_on", [])
    
    def build_tree(comp: str, depth: int = 0, visited: Set[str] = None) -> List[str]:
        if visited is None:
            visited = set()
        
        if depth > max_depth or comp in visited:
            return []
        
        visited.add(comp)
        lines = []
        
        prefix = "  " * depth + ("└── " if depth > 0 else "")
        lines.append(f"{prefix}{comp}")
        
        component_deps = sorted(deps_map.get(comp, []))
        for i, dep in enumerate(component_deps):
            is_last = i == len(component_deps) - 1
            sub_prefix = "  " * (depth + 1) + ("└── " if is_last else "├── ")
            sub_tree = build_tree(dep, depth + 1, visited.copy())
            if sub_tree:
                lines.append(sub_tree[0])
                lines.extend(sub_tree[1:])
        
        return lines
    
    return "\n".join(build_tree(component))

