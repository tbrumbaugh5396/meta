"""Dependency graph visualization and analysis."""

import json
from pathlib import Path
from typing import Dict, Any, List, Set, Optional
from meta.utils.manifest import get_components
from meta.utils.dependencies import get_component_dependencies, resolve_transitive_dependencies
from meta.utils.logger import log


def build_component_graph(manifests_dir: str = "manifests") -> Dict[str, List[str]]:
    """Build a dependency graph from components."""
    components = get_components(manifests_dir)
    graph = {}
    
    for name in components.keys():
        graph[name] = get_component_dependencies(name, components)
    
    return graph


def build_package_graph(component_dir: str) -> Dict[str, Any]:
    """Build dependency graph for package manager dependencies."""
    comp_path = Path(component_dir)
    graphs = {}
    
    # npm
    if (comp_path / "package.json").exists():
        graphs["npm"] = _build_npm_graph(component_dir)
    
    # pip
    if (comp_path / "requirements.txt").exists():
        graphs["pip"] = _build_pip_graph(component_dir)
    
    return graphs


def _build_npm_graph(component_dir: str) -> Dict[str, Any]:
    """Build npm dependency graph."""
    comp_path = Path(component_dir)
    package_json = comp_path / "package.json"
    
    if not package_json.exists():
        return {}
    
    try:
        with open(package_json) as f:
            pkg_data = json.load(f)
        
        graph = {
            "root": pkg_data.get("name", "root"),
            "dependencies": {}
        }
        
        # Direct dependencies
        deps = pkg_data.get("dependencies", {})
        dev_deps = pkg_data.get("devDependencies", {})
        
        for dep_name, dep_version in {**deps, **dev_deps}.items():
            graph["dependencies"][dep_name] = {
                "version": dep_version,
                "type": "dependency" if dep_name in deps else "devDependency"
            }
        
        return graph
    except Exception as e:
        log(f"Failed to build npm graph: {e}")
        return {}


def _build_pip_graph(component_dir: str) -> Dict[str, Any]:
    """Build pip dependency graph."""
    comp_path = Path(component_dir)
    requirements_txt = comp_path / "requirements.txt"
    
    if not requirements_txt.exists():
        return {}
    
    try:
        graph = {
            "root": "requirements.txt",
            "dependencies": {}
        }
        
        with open(requirements_txt) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Parse requirement line (simplified)
                    parts = line.split("==")
                    if len(parts) == 2:
                        dep_name = parts[0].strip()
                        dep_version = parts[1].strip()
                        graph["dependencies"][dep_name] = {
                            "version": dep_version,
                            "type": "requirement"
                        }
        
        return graph
    except Exception as e:
        log(f"Failed to build pip graph: {e}")
        return {}


def export_graph_dot(graph: Dict[str, List[str]], output_file: str) -> bool:
    """Export dependency graph to Graphviz DOT format."""
    try:
        with open(output_file, 'w') as f:
            f.write("digraph Dependencies {\n")
            f.write("  rankdir=LR;\n")
            f.write("  node [shape=box];\n\n")
            
            for node, deps in graph.items():
                for dep in deps:
                    f.write(f'  "{node}" -> "{dep}";\n')
            
            f.write("}\n")
        
        return True
    except Exception as e:
        log(f"Failed to export graph: {e}")
        return False


def export_graph_json(graph: Dict[str, List[str]], output_file: str) -> bool:
    """Export dependency graph to JSON format."""
    try:
        with open(output_file, 'w') as f:
            json.dump(graph, f, indent=2)
        return True
    except Exception as e:
        log(f"Failed to export graph: {e}")
        return False


