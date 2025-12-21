"""Dependency graph visualization commands."""

import typer
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List, Set
from meta.utils.logger import log, success, error, table, panel
from meta.utils.visualization import generate_dot_graph, generate_mermaid_graph, generate_text_tree
from meta.utils.manifest import get_components, find_meta_repo_root

app = typer.Typer(help="Dependency graph visualization")


@app.command()
def component(
    component_name: str = typer.Argument(..., help="Component name"),
    format: str = typer.Option("text", "--format", "-f", help="Output format (text, dot, mermaid)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Show dependency graph for a component."""
    if format == "text":
        graph = generate_text_tree(component_name, manifests_dir=manifests_dir)
    elif format == "dot":
        graph = generate_dot_graph(manifests_dir=manifests_dir)
    elif format == "mermaid":
        graph = generate_mermaid_graph(manifests_dir=manifests_dir)
    else:
        error(f"Unsupported format: {format}")
        raise typer.Exit(code=1)
    
    if output:
        Path(output).write_text(graph)
        success(f"Graph written to: {output}")
    else:
        print(graph)


@app.command()
def all(
    format: str = typer.Option("dot", "--format", "-f", help="Output format (dot, mermaid)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Show dependency graph for all components."""
    if format == "dot":
        graph = generate_dot_graph(manifests_dir=manifests_dir)
    elif format == "mermaid":
        graph = generate_mermaid_graph(manifests_dir=manifests_dir)
    else:
        error(f"Unsupported format for all components: {format}")
        raise typer.Exit(code=1)
    
    if output:
        Path(output).write_text(graph)
        success(f"Graph written to: {output}")
    else:
        print(graph)


def find_recursive_dependencies(
    target_repo: str,
    target_components: Dict[str, Any],
    all_meta_repos: Dict[str, Dict[str, Any]],
    meta_repo_names: List[str],
    visited: Optional[Set[str]] = None,
    depth: int = 0,
    max_depth: int = 100
) -> List[Dict[str, Any]]:
    """Recursively find all dependencies (down the graph)."""
    if visited is None:
        visited = set()
    
    if depth > max_depth:
        return []
    
    dependencies = []
    
    # Find direct dependencies
    for comp_name, comp_data in target_components.items():
        deps = comp_data.get("depends_on", [])
        for dep in deps:
            # Avoid cycles
            dep_key = f"{target_repo}:{comp_name}:{dep}"
            if dep_key in visited:
                continue
            visited.add(dep_key)
            
            # Check if dependency is a meta-repo or component
            dep_type = "component"
            dep_repo = None
            
            if dep in meta_repo_names:
                dep_type = "meta-repo"
                dep_repo = dep
            else:
                # Find which meta-repo contains this component
                for repo_name, repo_data in all_meta_repos.items():
                    if dep in repo_data.get("components", {}):
                        dep_repo = repo_name
                        dep_type = "component"
                        break
            
            dependencies.append({
                "type": dep_type,
                "name": dep,
                "used_by": comp_name,
                "in_repo": target_repo,
                "depth": depth,
                "source_repo": dep_repo
            })
            
            # Recursively find dependencies of this dependency
            if dep_repo and dep_repo in all_meta_repos:
                dep_components = all_meta_repos[dep_repo].get("components", {})
                if dep in dep_components:
                    # If it's a component, get its dependencies
                    transitive = find_recursive_dependencies(
                        dep_repo,
                        {dep: dep_components[dep]},
                        all_meta_repos,
                        meta_repo_names,
                        visited,
                        depth + 1,
                        max_depth
                    )
                    dependencies.extend(transitive)
                elif dep_type == "meta-repo":
                    # If it's a meta-repo, get all its components' dependencies
                    transitive = find_recursive_dependencies(
                        dep_repo,
                        dep_components,
                        all_meta_repos,
                        meta_repo_names,
                        visited,
                        depth + 1,
                        max_depth
                    )
                    dependencies.extend(transitive)
    
    return dependencies


def find_recursive_dependents(
    target_repo: str,
    target_components: Dict[str, Any],
    all_meta_repos: Dict[str, Dict[str, Any]],
    meta_repo_names: List[str],
    visited: Optional[Set[str]] = None,
    depth: int = 0,
    max_depth: int = 100
) -> List[Dict[str, Any]]:
    """Recursively find all dependents (up the graph)."""
    if visited is None:
        visited = set()
    
    if depth > max_depth:
        return []
    
    dependents = []
    
    # Find direct dependents
    for repo_name_check, repo_data in all_meta_repos.items():
        if repo_name_check == target_repo:
            continue
        
        components = repo_data.get("components", {})
        for comp_name, comp_data in components.items():
            deps = comp_data.get("depends_on", [])
            
            # Check if this component depends on target_repo as a meta-repo
            target_variants = [
                target_repo,
                target_repo.replace("-meta", ""),
                target_repo.replace("-platform-meta", "-platform"),
                target_repo.replace("-platform-meta", "")
            ]
            
            depends_on_target = False
            for variant in target_variants:
                if variant in deps:
                    dep_key = f"{repo_name_check}:{comp_name}:{target_repo}"
                    if dep_key not in visited:
                        visited.add(dep_key)
                        dependents.append({
                            "type": "meta-repo",
                            "name": repo_name_check,
                            "component": comp_name,
                            "depends_on": target_repo,
                            "depth": depth
                        })
                        depends_on_target = True
                    break
            
            # Check if this component depends on any component from target_repo
            for dep in deps:
                if dep in target_components:
                    dep_key = f"{repo_name_check}:{comp_name}:{dep}"
                    if dep_key not in visited:
                        visited.add(dep_key)
                        dependents.append({
                            "type": "component",
                            "name": dep,
                            "used_by": comp_name,
                            "in_repo": repo_name_check,
                            "defined_in": target_repo,
                            "depth": depth
                        })
                        depends_on_target = True
            
            # Recursively find dependents of this dependent
            if depends_on_target and repo_name_check in all_meta_repos:
                transitive = find_recursive_dependents(
                    repo_name_check,
                    all_meta_repos[repo_name_check].get("components", {}),
                    all_meta_repos,
                    meta_repo_names,
                    visited,
                    depth + 1,
                    max_depth
                )
                dependents.extend(transitive)
    
    return dependents


def find_connected_graph(
    target_repo: str,
    target_components: Dict[str, Any],
    all_meta_repos: Dict[str, Dict[str, Any]],
    meta_repo_names: List[str],
    max_depth: int = 100
) -> Dict[str, Any]:
    """Find the full connected graph: parents, children, and siblings."""
    # 1. Find all dependencies (children) recursively
    children = find_recursive_dependencies(
        target_repo,
        target_components,
        all_meta_repos,
        meta_repo_names,
        visited=set(),
        max_depth=max_depth
    )
    
    # 2. Find all dependents (parents) recursively
    parents = find_recursive_dependents(
        target_repo,
        target_components,
        all_meta_repos,
        meta_repo_names,
        visited=set(),
        max_depth=max_depth
    )
    
    # 3. Find siblings (components that share dependencies with target)
    siblings = []
    
    # Get all dependencies of target (direct and transitive)
    target_deps = set()
    for comp_name, comp_data in target_components.items():
        deps = comp_data.get("depends_on", [])
        target_deps.update(deps)
        # Also add transitive deps from children
        for child in children:
            if child.get("used_by") == comp_name:
                target_deps.add(child["name"])
    
    # Find components that depend on the same things target depends on
    for repo_name, repo_data in all_meta_repos.items():
        if repo_name == target_repo:
            continue
        
        components = repo_data.get("components", {})
        for comp_name, comp_data in components.items():
            comp_deps = set(comp_data.get("depends_on", []))
            
            # Check if this component shares any dependencies with target
            shared_deps = comp_deps.intersection(target_deps)
            if shared_deps:
                # Also check if this component is a sibling by being in the same dependency chain
                for shared_dep in shared_deps:
                    # Avoid duplicates
                    sibling_key = f"{repo_name}:{comp_name}:{shared_dep}"
                    if not any(s.get("key") == sibling_key for s in siblings):
                        siblings.append({
                            "type": "component",
                            "name": comp_name,
                            "in_repo": repo_name,
                            "shared_dependency": shared_dep,
                            "relationship": "sibling",
                            "key": sibling_key
                        })
    
    # 4. Build unified graph structure
    all_nodes = set()
    all_nodes.add(target_repo)
    
    # Add children
    for child in children:
        all_nodes.add(child["name"])
        if child.get("source_repo"):
            all_nodes.add(child["source_repo"])
    
    # Add parents
    for parent in parents:
        all_nodes.add(parent["name"])
        if parent.get("in_repo"):
            all_nodes.add(parent["in_repo"])
    
    # Add siblings
    for sibling in siblings:
        all_nodes.add(sibling["name"])
        if sibling.get("in_repo"):
            all_nodes.add(sibling["in_repo"])
        if sibling.get("shared_dependency"):
            all_nodes.add(sibling["shared_dependency"])
    
    return {
        "target": target_repo,
        "children": children,
        "parents": parents,
        "siblings": siblings,
        "all_nodes": list(all_nodes)
    }


def find_complete_connected_graph(
    target_repo: str,
    target_components: Dict[str, Any],
    all_meta_repos: Dict[str, Dict[str, Any]],
    meta_repo_names: List[str],
    max_depth: int = 100,
    include_components: bool = False
) -> Dict[str, Any]:
    """Find the complete connected graph: recursively expand all parents, children, siblings, and their connections.
    
    If include_components is True, also treats components as first-class nodes and expands their relationships.
    """
    all_relationships = []
    visited_repos = set()
    visited_components = set() if include_components else None
    queue = [(target_repo, "target", 0)]  # (node_name, relationship_type, depth, is_component)
    visited_repos.add(target_repo)
    
    # Build a map of all components to their repos for quick lookup
    component_to_repo = {}
    component_data_map = {}  # Map component name to its full data
    for repo_name, repo_data in all_meta_repos.items():
        components = repo_data.get("components", {})
        for comp_name, comp_data in components.items():
            component_to_repo[comp_name] = repo_name
            component_data_map[comp_name] = comp_data
    
    # Build dependency map for each repo (for sibling detection)
    repo_dependencies = {}
    repo_all_deps = {}  # Track all dependencies (direct + transitive) for better sibling detection
    
    def get_all_dependencies(repo_name: str, visited: set = None, current_depth: int = 0, max_dep_depth: int = 10) -> set:
        """Get all dependencies (direct + transitive) for a repo, with depth limit."""
        if visited is None:
            visited = set()
        # Check depth limit (skip if unlimited is effectively set via very large number)
        if repo_name in visited or (max_dep_depth < 999999 and current_depth > max_dep_depth):
            return set()
        visited.add(repo_name)
        
        all_deps = set()
        components = all_meta_repos.get(repo_name, {}).get("components", {})
        for comp_name, comp_data in components.items():
            deps = comp_data.get("depends_on", [])
            for dep in deps:
                all_deps.add(dep)
                # If it's a meta-repo dependency, get its transitive deps (with depth limit)
                if dep in meta_repo_names:
                    transitive = get_all_dependencies(dep, visited.copy(), current_depth + 1, max_dep_depth)
                    all_deps.update(transitive)
                elif dep in component_to_repo:
                    dep_repo = component_to_repo[dep]
                    if dep_repo != repo_name:
                        transitive = get_all_dependencies(dep_repo, visited.copy(), current_depth + 1, max_dep_depth)
                        all_deps.update(transitive)
        return all_deps
    
    # Build dependency maps with depth limit (use smaller limit for dependency map building)
    # Cap at 10 for dependency map to avoid excessive computation, unless unlimited
    if max_depth >= 999999:
        dep_map_max_depth = 999999  # Unlimited
    else:
        dep_map_max_depth = min(max_depth, 10)  # Cap at 10 for dependency map
    
    for repo_name, repo_data in all_meta_repos.items():
        deps = set()
        components = repo_data.get("components", {})
        for comp_name, comp_data in components.items():
            deps.update(comp_data.get("depends_on", []))
        repo_dependencies[repo_name] = deps
        repo_all_deps[repo_name] = get_all_dependencies(repo_name, max_dep_depth=dep_map_max_depth)
    
    # Breadth-first traversal to find entire connected component
    while queue:
        current_node, relationship, depth = queue.pop(0)
        
        # Check depth limit (skip if unlimited is effectively set via very large number)
        if max_depth < 999999 and depth > max_depth:
            continue
        
        # Determine if current node is a component or repo
        is_component = include_components and current_node in component_data_map
        current_repo = current_node if not is_component else component_to_repo.get(current_node)
        
        if is_component:
            # Processing a component node
            current_component = current_node
            current_component_data = component_data_map.get(current_component, {})
            current_component_deps = set(current_component_data.get("depends_on", []))
            
            # 1. Add "contains" relationship (repo -> component) if not already added
            if current_repo and current_component not in visited_components:
                visited_components.add(current_component)
                all_relationships.append({
                    "type": "contains",
                    "from_repo": current_repo,
                    "to_component": current_component,
                    "depth": depth
                })
            
            # 2. Find component dependencies (component -> component or component -> repo)
            for dep in current_component_deps:
                # Check if dependency is a component
                if dep in component_data_map:
                    # Component depends on another component
                    dep_repo = component_to_repo.get(dep)
                    all_relationships.append({
                        "type": "component_depends",
                        "from_component": current_component,
                        "to_component": dep,
                        "from_repo": current_repo,
                        "to_repo": dep_repo,
                        "depth": depth
                    })
                    
                    # Add dependent component to queue if not visited
                    if dep not in visited_components:
                        visited_components.add(dep)
                        queue.append((dep, "component", depth + 1))
                
                # Check if dependency is a meta-repo
                elif dep in meta_repo_names:
                    # Component depends on a meta-repo
                    all_relationships.append({
                        "type": "component_depends_repo",
                        "from_component": current_component,
                        "from_repo": current_repo,
                        "to_repo": dep,
                        "depth": depth
                    })
                    
                    # Add repo to queue if not visited
                    if dep not in visited_repos:
                        visited_repos.add(dep)
                        queue.append((dep, "child", depth + 1))
            
            # 3. Find which repos/components use this component
            for repo_name_check, repo_data in all_meta_repos.items():
                components_check = repo_data.get("components", {})
                for comp_name_check, comp_data_check in components_check.items():
                    deps_check = comp_data_check.get("depends_on", [])
                    if current_component in deps_check:
                        # Component is used by another component
                        all_relationships.append({
                            "type": "component_used_by",
                            "from_component": comp_name_check,
                            "from_repo": repo_name_check,
                            "to_component": current_component,
                            "to_repo": current_repo,
                            "depth": depth
                        })
                        
                        # Add using component/repo to queue
                        if comp_name_check not in visited_components:
                            visited_components.add(comp_name_check)
                            queue.append((comp_name_check, "component", depth + 1))
                        if repo_name_check not in visited_repos:
                            visited_repos.add(repo_name_check)
                            queue.append((repo_name_check, "parent", depth + 1))
            
            # Continue to next iteration (component processing done)
            continue
        
        # Processing a repo node (existing logic)
        current_components = all_meta_repos.get(current_repo, {}).get("components", {})
        current_deps = repo_dependencies.get(current_repo, set())
        current_all_deps = repo_all_deps.get(current_repo, set())
        
        # If including components, add component nodes for this repo
        if include_components:
            for comp_name in current_components.keys():
                if comp_name not in visited_components:
                    visited_components.add(comp_name)
                    all_relationships.append({
                        "type": "contains",
                        "from_repo": current_repo,
                        "to_component": comp_name,
                        "depth": depth
                    })
                    # Add component to queue for expansion
                    queue.append((comp_name, "component", depth))
        
        # 1. Find all dependencies (children) of current repo
        for comp_name, comp_data in current_components.items():
            deps = comp_data.get("depends_on", [])
            for dep in deps:
                dep_repo = None
                dep_type = "component"
                
                if dep in meta_repo_names:
                    dep_type = "meta-repo"
                    dep_repo = dep
                elif dep in component_to_repo:
                    dep_repo = component_to_repo[dep]
                    dep_type = "component"
                
                # Skip self-dependencies (component depending on another component in same repo)
                if dep_repo and dep_repo != current_repo:
                    # Record relationship (even if already visited, to show all relationships)
                    all_relationships.append({
                        "type": "child",
                        "from_repo": current_repo,
                        "from_component": comp_name,
                        "to_repo": dep_repo,
                        "to_component": dep if dep_type == "component" else None,
                        "relationship_type": dep_type,
                        "depth": depth
                    })
                    
                    # Add to queue if not visited (to expand further)
                    if dep_repo not in visited_repos:
                        visited_repos.add(dep_repo)
                        queue.append((dep_repo, "child", depth + 1))
        
        # 2. Find all dependents (parents) of current repo
        for repo_name_check, repo_data in all_meta_repos.items():
            if repo_name_check == current_repo:
                continue
            
            components = repo_data.get("components", {})
            depends_on_current = False
            
            for comp_name, comp_data in components.items():
                deps = comp_data.get("depends_on", [])
                
                # Check if this component depends on current_repo
                target_variants = [
                    current_repo,
                    current_repo.replace("-meta", ""),
                    current_repo.replace("-platform-meta", "-platform"),
                    current_repo.replace("-platform-meta", "")
                ]
                
                for variant in target_variants:
                    if variant in deps:
                        depends_on_current = True
                        break
                
                # Also check if component depends on any component from current_repo
                if not depends_on_current:
                    for dep in deps:
                        if dep in current_components:
                            depends_on_current = True
                            break
                
                if depends_on_current:
                    # Record relationship (even if already visited)
                    all_relationships.append({
                        "type": "parent",
                        "from_repo": repo_name_check,
                        "from_component": comp_name,
                        "to_repo": current_repo,
                        "to_component": None,
                        "relationship_type": "meta-repo",
                        "depth": depth
                    })
                    
                    # Add to queue if not visited (to expand further)
                    if repo_name_check not in visited_repos:
                        visited_repos.add(repo_name_check)
                        queue.append((repo_name_check, "parent", depth + 1))
                    break
        
        # 3. Find siblings (repos that share dependencies with current repo) and expand them
        # Use both direct and transitive dependencies for better sibling detection
        for repo_name_check, repo_data in all_meta_repos.items():
            if repo_name_check == current_repo or repo_name_check not in all_meta_repos:
                continue
            
            check_deps = repo_dependencies.get(repo_name_check, set())
            check_all_deps = repo_all_deps.get(repo_name_check, set())
            
            # Check for shared dependencies (both direct and transitive)
            shared_deps = current_deps.intersection(check_deps)
            shared_all_deps = current_all_deps.intersection(check_all_deps)
            
            # If they share any dependencies (direct or transitive), they're siblings
            if shared_deps or shared_all_deps:
                # Use direct deps if available, otherwise use transitive
                final_shared_deps = shared_deps if shared_deps else shared_all_deps
                
                # Record sibling relationship
                all_relationships.append({
                    "type": "sibling",
                    "repo1": current_repo,
                    "repo2": repo_name_check,
                    "shared_dependencies": list(final_shared_deps),
                    "depth": depth
                })
                
                # Add sibling to queue for expansion (this ensures we explore its children/parents)
                if repo_name_check not in visited_repos:
                    visited_repos.add(repo_name_check)
                    queue.append((repo_name_check, "sibling", depth + 1))
    
    # Organize results by relationship type
    children = [r for r in all_relationships if r["type"] == "child"]
    parents = [r for r in all_relationships if r["type"] == "parent"]
    siblings = [r for r in all_relationships if r["type"] == "sibling"]
    
    # Component relationships
    contains = [r for r in all_relationships if r["type"] == "contains"] if include_components else []
    component_depends = [r for r in all_relationships if r["type"] == "component_depends"] if include_components else []
    component_depends_repo = [r for r in all_relationships if r["type"] == "component_depends_repo"] if include_components else []
    component_used_by = [r for r in all_relationships if r["type"] == "component_used_by"] if include_components else []
    
    # Build all nodes set
    all_nodes = set(visited_repos)
    component_nodes = set(visited_components) if include_components else set()
    
    for rel in all_relationships:
        if rel.get("to_repo"):
            all_nodes.add(rel["to_repo"])
        if rel.get("from_repo"):
            all_nodes.add(rel["from_repo"])
        if rel.get("repo1"):
            all_nodes.add(rel["repo1"])
        if rel.get("repo2"):
            all_nodes.add(rel["repo2"])
    
    return {
        "target": target_repo,
        "children": children,
        "parents": parents,
        "siblings": siblings,
        "all_nodes": list(all_nodes),
        "component_nodes": list(component_nodes) if include_components else [],
        "contains": contains,
        "component_depends": component_depends,
        "component_depends_repo": component_depends_repo,
        "component_used_by": component_used_by,
        "all_relationships": all_relationships,
        "component_to_repo": component_to_repo
    }


@app.command(name="meta-repo")
def meta_repo_graph(
    repo_name: Optional[str] = typer.Option(None, "--repo", "-r", help="Specific meta-repo to analyze (default: current)"),
    direction: str = typer.Option("both", "--direction", "-d", help="Direction: 'up' (dependents), 'down' (dependencies), 'both'"),
    format: str = typer.Option("text", "--format", "-f", help="Output format (text, dot, mermaid)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
    recursive: bool = typer.Option(False, "--recursive", help="Recursively traverse the graph (up and down)"),
    recursive_up: bool = typer.Option(False, "--recursive-up", help="Recursively traverse up (dependents)"),
    recursive_down: bool = typer.Option(False, "--recursive-down", help="Recursively traverse down (dependencies)"),
    max_depth: int = typer.Option(100, "--max-depth", help="Maximum recursion depth (default: 100)"),
):
    """Show meta-repo dependency graph (which meta-repos use this, which this uses)."""
    # Find current meta-repo
    current_root = find_meta_repo_root()
    if not current_root:
        error("Could not find meta-repo root. Run from a meta-repo directory.")
        raise typer.Exit(code=1)
    
    workspace_root = current_root.parent
    current_repo_name = current_root.name
    
    # Determine which repo to analyze
    target_repo = repo_name or current_repo_name
    target_path = workspace_root / target_repo
    
    if not target_path.exists():
        error(f"Meta-repo '{target_repo}' not found at {target_path}")
        raise typer.Exit(code=1)
    
    # Scan all meta-repos in workspace
    meta_repo_names = ["meta-repo", "gambling-platform-meta", "scraping-platform-meta", "platform-meta"]
    all_meta_repos: Dict[str, Dict[str, Any]] = {}
    
    for repo_name_check in meta_repo_names:
        repo_path = workspace_root / repo_name_check
        if repo_path.exists() and (repo_path / "manifests" / "components.yaml").exists():
            try:
                components = get_components(str(repo_path / "manifests"))
                all_meta_repos[repo_name_check] = {
                    "path": repo_path,
                    "components": components
                }
            except Exception as e:
                log(f"Warning: Could not load {repo_name_check}: {e}")
    
    # Build dependency graph
    dependents: List[Dict[str, Any]] = []  # Meta-repos/components that depend on target_repo
    dependencies: List[Dict[str, Any]] = []  # Meta-repos/components that target_repo depends on
    
    # Determine if we should use recursive traversal
    use_recursive = recursive or recursive_up or recursive_down
    
    # Get target repo's components
    target_components = all_meta_repos.get(target_repo, {}).get("components", {})
    
    # Find dependencies (what target_repo uses)
    if direction in ("down", "both"):
        if use_recursive and (recursive or recursive_down):
            dependencies = find_recursive_dependencies(
                target_repo,
                target_components,
                all_meta_repos,
                meta_repo_names,
                max_depth=max_depth
            )
        else:
            # Original non-recursive logic
            for comp_name, comp_data in target_components.items():
                deps = comp_data.get("depends_on", [])
                for dep in deps:
                    # Check if dependency is a meta-repo or component
                    dep_type = "component"
                    if dep in meta_repo_names:
                        dep_type = "meta-repo"
                    elif any(dep in all_meta_repos.get(repo, {}).get("components", {}) for repo in meta_repo_names):
                        dep_type = "component"
                    
                    dependencies.append({
                        "type": dep_type,
                        "name": dep,
                        "used_by": comp_name,
                        "in_repo": target_repo,
                        "depth": 0
                    })
    
    # Find dependents (what uses target_repo)
    if direction in ("up", "both"):
        if use_recursive and (recursive or recursive_up):
            dependents = find_recursive_dependents(
                target_repo,
                target_components,
                all_meta_repos,
                meta_repo_names,
                max_depth=max_depth
            )
        else:
            # Original non-recursive logic
            for repo_name_check, repo_data in all_meta_repos.items():
                if repo_name_check == target_repo:
                    continue
                
                components = repo_data.get("components", {})
                for comp_name, comp_data in components.items():
                    deps = comp_data.get("depends_on", [])
                    
                    # Check if this component depends on target_repo as a meta-repo
                    # Handle both "scraping-platform" and "scraping-platform-meta" variations
                    target_variants = [
                        target_repo,
                        target_repo.replace("-meta", ""),
                        target_repo.replace("-platform-meta", "-platform"),
                        target_repo.replace("-platform-meta", "")
                    ]
                    
                    for variant in target_variants:
                        if variant in deps:
                            dependents.append({
                                "type": "meta-repo",
                                "name": repo_name_check,
                                "component": comp_name,
                                "depends_on": target_repo,
                                "depth": 0
                            })
                            break
                    
                    # Check if this component depends on any component from target_repo
                    for dep in deps:
                        if dep in target_components:
                            dependents.append({
                                "type": "component",
                                "name": dep,
                                "used_by": comp_name,
                                "in_repo": repo_name_check,
                                "defined_in": target_repo,
                                "depth": 0
                            })
    
    # Display results
    if format == "text":
        title_suffix = " (Recursive)" if use_recursive else ""
        panel(f"Meta-Repo Graph: {target_repo}{title_suffix}", "Graph Analysis")
        
        if direction in ("down", "both") and dependencies:
            log("\n📥 Dependencies (what this repo uses):")
            rows = []
            seen = set()
            # Sort by depth for better visualization
            sorted_deps = sorted(dependencies, key=lambda x: (x.get("depth", 0), x["name"]))
            for dep in sorted_deps:
                key = (dep["type"], dep["name"], dep.get("used_by"))
                if key not in seen:
                    seen.add(key)
                    depth_indicator = "  " * dep.get("depth", 0) + ("└─ " if dep.get("depth", 0) > 0 else "")
                    depth_str = str(dep.get("depth", 0)) if use_recursive else "N/A"
                    rows.append([
                        dep["type"],
                        depth_indicator + dep["name"],
                        dep.get("used_by", "N/A"),
                        dep.get("in_repo", target_repo),
                        depth_str
                    ])
            headers = ["Type", "Dependency", "Used By", "In Repo"]
            if use_recursive:
                headers.append("Depth")
            table(headers, rows)
        elif direction in ("down", "both"):
            log("\n📥 Dependencies: None")
        
        if direction in ("up", "both") and dependents:
            log("\n📤 Dependents (what uses this repo):")
            rows = []
            seen = set()
            # Sort by depth for better visualization
            sorted_deps = sorted(dependents, key=lambda x: (x.get("depth", 0), x["name"]))
            for dep in sorted_deps:
                if dep["type"] == "meta-repo":
                    key = (dep["type"], dep["name"], dep.get("component"))
                    if key not in seen:
                        seen.add(key)
                        depth_indicator = "  " * dep.get("depth", 0) + ("└─ " if dep.get("depth", 0) > 0 else "")
                        depth_str = str(dep.get("depth", 0)) if use_recursive else "N/A"
                        rows.append([
                            "meta-repo",
                            depth_indicator + dep["name"],
                            dep.get("component", "N/A"),
                            "N/A",
                            depth_str
                        ])
                else:
                    key = (dep["type"], dep["name"], dep.get("used_by"))
                    if key not in seen:
                        seen.add(key)
                        depth_indicator = "  " * dep.get("depth", 0) + ("└─ " if dep.get("depth", 0) > 0 else "")
                        depth_str = str(dep.get("depth", 0)) if use_recursive else "N/A"
                        rows.append([
                            "component",
                            depth_indicator + dep["name"],
                            dep.get("used_by", "N/A"),
                            dep.get("in_repo", "N/A"),
                            depth_str
                        ])
            headers = ["Type", "Dependent", "Component", "In Repo"]
            if use_recursive:
                headers.append("Depth")
            table(headers, rows)
        elif direction in ("up", "both"):
            log("\n📤 Dependents: None")
        
        if not dependencies and not dependents:
            log(f"\n{target_repo} has no dependencies or dependents.")
    
    elif format == "dot":
        # Generate DOT graph
        dot_lines = ["digraph MetaRepoGraph {", "  rankdir=LR;", "  node [shape=box];", ""]
        
        # Add nodes
        dot_lines.append(f'  "{target_repo}" [style=filled, fillcolor=lightblue];')
        seen_nodes = {target_repo}
        
        for dep in dependencies:
            if dep["name"] not in seen_nodes:
                seen_nodes.add(dep["name"])
                if dep["type"] == "meta-repo":
                    dot_lines.append(f'  "{dep["name"]}" [style=filled, fillcolor=lightgreen];')
                else:
                    dot_lines.append(f'  "{dep["name"]}" [shape=ellipse];')
        
        for dep in dependents:
            if dep["type"] == "meta-repo" and dep["name"] not in seen_nodes:
                seen_nodes.add(dep["name"])
                dot_lines.append(f'  "{dep["name"]}" [style=filled, fillcolor=lightgreen];')
            elif dep["name"] not in seen_nodes:
                seen_nodes.add(dep["name"])
                dot_lines.append(f'  "{dep["name"]}" [shape=ellipse];')
        
        dot_lines.append("")
        
        # Add edges (dependencies)
        for dep in dependencies:
            dot_lines.append(f'  "{target_repo}" -> "{dep["name"]}" [label="uses"];')
        
        # Add edges (dependents)
        for dep in dependents:
            if dep["type"] == "meta-repo":
                dot_lines.append(f'  "{dep["name"]}" -> "{target_repo}" [label="depends on"];')
            else:
                dot_lines.append(f'  "{dep["name"]}" -> "{target_repo}" [label="defined in"];')
        
        dot_lines.append("}")
        graph_output = "\n".join(dot_lines)
        
        if output:
            Path(output).write_text(graph_output)
            success(f"Graph written to: {output}")
        else:
            print(graph_output)
    
    elif format == "mermaid":
        # Generate Mermaid graph
        mermaid_lines = ["graph LR", ""]
        
        # Add nodes
        mermaid_lines.append(f'  {target_repo.replace("-", "_")}["{target_repo}"]')
        seen_nodes = {target_repo}
        
        for dep in dependencies:
            node_id = dep["name"].replace("-", "_")
            if dep["name"] not in seen_nodes:
                seen_nodes.add(dep["name"])
                mermaid_lines.append(f'  {node_id}["{dep["name"]}"]')
        
        for dep in dependents:
            node_id = dep["name"].replace("-", "_")
            if dep["name"] not in seen_nodes:
                seen_nodes.add(dep["name"])
                mermaid_lines.append(f'  {node_id}["{dep["name"]}"]')
        
        mermaid_lines.append("")
        
        # Add edges
        target_id = target_repo.replace("-", "_")
        for dep in dependencies:
            dep_id = dep["name"].replace("-", "_")
            mermaid_lines.append(f'  {target_id} -->|uses| {dep_id}')
        
        for dep in dependents:
            dep_id = dep["name"].replace("-", "_")
            mermaid_lines.append(f'  {dep_id} -->|depends on| {target_id}')
        
        graph_output = "\n".join(mermaid_lines)
        
        if output:
            Path(output).write_text(graph_output)
            success(f"Graph written to: {output}")
        else:
            print(graph_output)
    
    else:
        error(f"Unsupported format: {format}")
        raise typer.Exit(code=1)


def calculate_repo_ranks(graph: Dict[str, Any], meta_repo_names: List[str]) -> Dict[str, int]:
    """Calculate dependency rank for each repo (higher = more dependencies/used by more)."""
    repo_scores = {}
    
    for repo in graph["all_nodes"]:
        if repo not in meta_repo_names:
            continue
        
        # Count how many repos depend on this one (incoming)
        incoming = sum(1 for rel in graph["parents"] if rel.get("to_repo") == repo)
        # Count how many repos this one depends on (outgoing)
        outgoing = sum(1 for rel in graph["children"] if rel.get("from_repo") == repo)
        
        # Score = incoming - outgoing (higher = more foundational/depended upon)
        repo_scores[repo] = incoming - outgoing
    
    return repo_scores


def export_mermaid_to_image(
    mermaid_content: str,
    output_path: Path,
    format: str = "pdf",
    width: int = 2400,
    height: int = 1800
) -> bool:
    """Export Mermaid diagram to PDF, PNG, or SVG using mermaid-cli."""
    import subprocess
    import tempfile
    import shutil
    
    # Check if mmdc (mermaid-cli) is available
    mmdc_path = shutil.which("mmdc")
    if not mmdc_path:
        # Try npx mmdc as fallback
        if shutil.which("npx"):
            mmdc_path = "npx"
            use_npx = True
        else:
            error("mermaid-cli (mmdc) is not installed.")
            error("Install it with: npm install -g @mermaid-js/mermaid-cli")
            error("Or use npx: npx @mermaid-js/mermaid-cli")
            return False
    else:
        use_npx = False
    
    # Create temporary file for Mermaid content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as tmp_file:
        tmp_file.write(mermaid_content)
        tmp_mmd_path = tmp_file.name
    
    try:
        # Build command
        if use_npx:
            cmd = [
                "npx", "-y", "@mermaid-js/mermaid-cli",
                "-i", tmp_mmd_path,
                "-o", str(output_path),
                "-w", str(width),
                "-H", str(height),
                "-e", format.lower()
            ]
        else:
            cmd = [
                mmdc_path,
                "-i", tmp_mmd_path,
                "-o", str(output_path),
                "-w", str(width),
                "-H", str(height),
                "-e", format.lower()
            ]
        
        # Run mermaid-cli
        log(f"Exporting Mermaid diagram to {format.upper()}...")
        log(f"Using command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # Increased timeout for npx downloads
        )
        
        if result.returncode == 0:
            success(f"Mermaid diagram exported to: {output_path}")
            return True
        else:
            error(f"Failed to export Mermaid diagram: {result.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        error("Mermaid export timed out")
        return False
    except Exception as e:
        error(f"Error exporting Mermaid diagram: {e}")
        return False
    finally:
        # Clean up temporary file
        try:
            Path(tmp_mmd_path).unlink()
        except Exception:
            pass


@app.command(name="full")
def full_graph(
    repo_name: Optional[str] = typer.Option(None, "--repo", "-r", help="Specific meta-repo to analyze (default: current)"),
    format: str = typer.Option("text", "--format", "-f", help="Output format (text, dot, mermaid)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
    max_depth: int = typer.Option(10, "--max-depth", help="Maximum recursion depth (default: 10)"),
    unlimited: bool = typer.Option(False, "--unlimited", "-u", help="Unlimited traversal depth (overrides --max-depth)"),
    show_components: bool = typer.Option(False, "--show-components", "-c", help="Show components as nodes with full recursive expansion"),
    sort_repos: str = typer.Option("none", "--sort-repos", help="Sort repos by dependency count: 'top' (highest at top), 'bottom' (highest at bottom), 'none' (default)"),
    repo_color: str = typer.Option("green", "--repo-color", help="Color for meta-repos (default: green)"),
    component_color: str = typer.Option("red", "--component-color", help="Color for components (default: red)"),
    component_level: str = typer.Option("bottom", "--component-level", help="Place all components at same level: 'top' or 'bottom' (default: bottom)"),
    export: Optional[str] = typer.Option(None, "--export", "-e", help="Export Mermaid to image: 'pdf', 'png', or 'svg' (requires mermaid-cli)"),
    image_width: int = typer.Option(2400, "--image-width", help="Image width in pixels (default: 2400)"),
    image_height: int = typer.Option(1800, "--image-height", help="Image height in pixels (default: 1800)"),
):
    """Show complete connected graph: recursively expand all parents, children, siblings, and their connections."""
    # Find current meta-repo
    current_root = find_meta_repo_root()
    if not current_root:
        error("Could not find meta-repo root. Run from a meta-repo directory.")
        raise typer.Exit(code=1)
    
    workspace_root = current_root.parent
    current_repo_name = current_root.name
    
    # Determine which repo to analyze
    target_repo = repo_name or current_repo_name
    target_path = workspace_root / target_repo
    
    if not target_path.exists():
        error(f"Meta-repo '{target_repo}' not found at {target_path}")
        raise typer.Exit(code=1)
    
    # Scan all meta-repos in workspace
    meta_repo_names = ["meta-repo", "gambling-platform-meta", "scraping-platform-meta", "platform-meta"]
    all_meta_repos: Dict[str, Dict[str, Any]] = {}
    
    for repo_name_check in meta_repo_names:
        repo_path = workspace_root / repo_name_check
        if repo_path.exists() and (repo_path / "manifests" / "components.yaml").exists():
            try:
                components = get_components(str(repo_path / "manifests"))
                all_meta_repos[repo_name_check] = {
                    "path": repo_path,
                    "components": components
                }
            except Exception as e:
                log(f"Warning: Could not load {repo_name_check}: {e}")
    
    # Get target repo's components
    target_components = all_meta_repos.get(target_repo, {}).get("components", {})
    
    # Handle unlimited depth
    if unlimited:
        effective_max_depth = 999999  # Very large number for unlimited
    else:
        effective_max_depth = max_depth
    
    # Find complete connected graph (with sibling expansion)
    graph = find_complete_connected_graph(
        target_repo,
        target_components,
        all_meta_repos,
        meta_repo_names,
        max_depth=effective_max_depth,
        include_components=show_components
    )
    
    # Display results
    if format == "text":
        panel(f"Complete Connected Graph: {graph['target']}", "Graph Analysis")
        
        log(f"\n📊 Total connected repos: {len(graph['all_nodes'])}")
        if show_components:
            log(f"   - Components: {len(graph.get('component_nodes', []))}")
        log(f"   - Children relationships: {len(graph['children'])}")
        log(f"   - Parent relationships: {len(graph['parents'])}")
        log(f"   - Sibling relationships: {len(graph['siblings'])}")
        if show_components:
            log(f"   - Component dependencies: {len(graph.get('component_depends', []))}")
            log(f"   - Component-to-repo: {len(graph.get('component_depends_repo', []))}")
            log(f"   - Components used by: {len(graph.get('component_used_by', []))}")
        
        # Show all repos in the connected component
        log("\n🔗 All Connected Repos:")
        for node in sorted(graph['all_nodes']):
            if node == graph['target']:
                log(f"   ⭐ {node} (target)")
            else:
                log(f"   • {node}")
        
        # Show components if enabled
        if show_components and graph.get('component_nodes'):
            log("\n🧩 Components:")
            # Group components by repo
            components_by_repo = {}
            for comp in graph['component_nodes']:
                repo = graph.get('component_to_repo', {}).get(comp, 'unknown')
                if repo not in components_by_repo:
                    components_by_repo[repo] = []
                components_by_repo[repo].append(comp)
            
            for repo in sorted(components_by_repo.keys()):
                log(f"   📦 {repo}:")
                for comp in sorted(components_by_repo[repo]):
                    log(f"      • {comp}")
        
        # Show children (dependencies)
        if graph["children"]:
            log("\n📥 Dependency Chains (children - what repos use):")
            rows = []
            seen = set()
            sorted_children = sorted(graph["children"], key=lambda x: (x.get("depth", 0), x.get("to_repo", "")))
            for child in sorted_children:
                key = (child.get("from_repo"), child.get("to_repo"), child.get("from_component"))
                if key not in seen:
                    seen.add(key)
                    depth_indicator = "  " * child.get("depth", 0) + ("└─ " if child.get("depth", 0) > 0 else "")
                    rows.append([
                        child.get("from_repo", "N/A"),
                        depth_indicator + child.get("to_repo", "N/A"),
                        child.get("from_component", "N/A"),
                        child.get("relationship_type", "N/A"),
                        str(child.get("depth", 0))
                    ])
            table(["From Repo", "To Repo (Dependency)", "Component", "Type", "Depth"], rows)
        else:
            log("\n📥 Children: None")
        
        # Show parents (dependents)
        if graph["parents"]:
            log("\n📤 Dependent Chains (parents - what uses these repos):")
            rows = []
            seen = set()
            sorted_parents = sorted(graph["parents"], key=lambda x: (x.get("depth", 0), x.get("from_repo", "")))
            for parent in sorted_parents:
                key = (parent.get("from_repo"), parent.get("to_repo"), parent.get("from_component"))
                if key not in seen:
                    seen.add(key)
                    depth_indicator = "  " * parent.get("depth", 0) + ("└─ " if parent.get("depth", 0) > 0 else "")
                    rows.append([
                        depth_indicator + parent.get("from_repo", "N/A"),
                        parent.get("to_repo", "N/A"),
                        parent.get("from_component", "N/A"),
                        str(parent.get("depth", 0))
                    ])
            table(["Dependent Repo", "Depends On", "Component", "Depth"], rows)
        else:
            log("\n📤 Parents: None")
        
        # Show siblings (repos that share dependencies)
        if graph["siblings"]:
            log("\n👥 Sibling Relationships (repos that share dependencies):")
            rows = []
            seen = set()
            for sibling in graph["siblings"]:
                key = (sibling.get("repo1"), sibling.get("repo2"))
                if key not in seen and (sibling.get("repo2"), sibling.get("repo1")) not in seen:
                    seen.add(key)
                    shared_deps = sibling.get("shared_dependencies", [])
                    shared_deps_str = ", ".join(shared_deps[:3])
                    if len(shared_deps) > 3:
                        shared_deps_str += f" (+{len(shared_deps) - 3} more)"
                    rows.append([
                        sibling.get("repo1", "N/A"),
                        sibling.get("repo2", "N/A"),
                        shared_deps_str or "N/A",
                        str(sibling.get("depth", 0))
                    ])
            table(["Repo 1", "Repo 2", "Shared Dependencies", "Depth"], rows)
        else:
            log("\n👥 Siblings: None")
        
        # Show component dependencies if enabled
        if show_components:
            if graph.get("component_depends"):
                log("\n🔗 Component Dependencies (component -> component):")
                rows = []
                seen = set()
                sorted_deps = sorted(graph["component_depends"], key=lambda x: (x.get("depth", 0), x.get("from_component", "")))
                for dep in sorted_deps:
                    key = (dep.get("from_component"), dep.get("to_component"))
                    if key not in seen:
                        seen.add(key)
                        depth_indicator = "  " * dep.get("depth", 0) + ("└─ " if dep.get("depth", 0) > 0 else "")
                        rows.append([
                            dep.get("from_component", "N/A"),
                            depth_indicator + dep.get("to_component", "N/A"),
                            dep.get("from_repo", "N/A"),
                            dep.get("to_repo", "N/A"),
                            str(dep.get("depth", 0))
                        ])
                table(["From Component", "To Component", "From Repo", "To Repo", "Depth"], rows)
            
            if graph.get("component_depends_repo"):
                log("\n🔗 Component to Repo Dependencies:")
                rows = []
                seen = set()
                for dep in graph["component_depends_repo"]:
                    key = (dep.get("from_component"), dep.get("to_repo"))
                    if key not in seen:
                        seen.add(key)
                        rows.append([
                            dep.get("from_component", "N/A"),
                            dep.get("to_repo", "N/A"),
                            dep.get("from_repo", "N/A"),
                            str(dep.get("depth", 0))
                        ])
                table(["Component", "Depends On Repo", "Component's Repo", "Depth"], rows)
            
            if graph.get("component_used_by"):
                log("\n📊 Components Used By:")
                rows = []
                seen = set()
                for used in graph["component_used_by"]:
                    key = (used.get("to_component"), used.get("from_component"))
                    if key not in seen:
                        seen.add(key)
                        rows.append([
                            used.get("to_component", "N/A"),
                            used.get("from_component", "N/A"),
                            used.get("from_repo", "N/A"),
                            used.get("to_repo", "N/A"),
                            str(used.get("depth", 0))
                        ])
                table(["Component", "Used By Component", "Used By Repo", "Component's Repo", "Depth"], rows)
    
    elif format == "dot":
        # Generate DOT graph with all relationships
        dot_lines = ["digraph CompleteConnectedGraph {", "  rankdir=TB;", "  node [shape=box];", ""]
        
        # Calculate repo ranks if sorting is enabled
        repo_ranks = {}
        sorted_repos = []
        if sort_repos != "none":
            repo_ranks = calculate_repo_ranks(graph, meta_repo_names)
            # Sort repos by rank
            sorted_repos = sorted(repo_ranks.items(), key=lambda x: x[1], reverse=(sort_repos == "top"))
        
        # Color mapping
        color_map = {
            "green": "lightgreen",
            "red": "lightcoral",
            "blue": "lightblue",
            "yellow": "lightyellow",
            "orange": "lightsalmon",
            "purple": "plum"
        }
        repo_fill_color = color_map.get(repo_color.lower(), repo_color)
        component_fill_color = color_map.get(component_color.lower(), component_color)
        
        # Add target node (highlighted, keep distinct from other repos)
        target_color = "lightblue"  # Keep target distinct
        dot_lines.append(f'  "{graph["target"]}" [style=filled, fillcolor={target_color}, shape=doubleoctagon];')
        seen_nodes = {graph["target"]}
        
        # Add repo nodes with colors (sorted if requested)
        repos_to_add = sorted(graph["all_nodes"], key=lambda x: repo_ranks.get(x, 0), reverse=(sort_repos == "top")) if sort_repos != "none" else graph["all_nodes"]
        
        for node in repos_to_add:
            if node not in seen_nodes and node != graph["target"]:
                seen_nodes.add(node)
                if node in meta_repo_names:
                    dot_lines.append(f'  "{node}" [style=filled, fillcolor={repo_fill_color}];')
                else:
                    dot_lines.append(f'  "{node}" [shape=box];')
        
        # Add component nodes if enabled
        component_nodes_list = []
        if show_components and graph.get('component_nodes'):
            dot_lines.append("")
            dot_lines.append("  // Component nodes")
            for comp in graph['component_nodes']:
                comp_id = comp.replace("-", "_").replace(" ", "_").replace(".", "_")
                if comp_id not in seen_nodes:
                    seen_nodes.add(comp_id)
                    dot_lines.append(f'  "{comp_id}" [label="{comp}", shape=ellipse, style=filled, fillcolor={component_fill_color}];')
                    component_nodes_list.append(f'"{comp_id}"')
        
        # Add rank constraints for component level placement
        if show_components and component_level in ("top", "bottom") and component_nodes_list:
            rank_type = "min" if component_level == "top" else "max"
            dot_lines.append(f'  {{rank={rank_type}; {" ".join(component_nodes_list)}}}')
        
        # Build sibling groups first (before sorting constraints)
        sibling_groups = []  # List of sets, each set contains repos that are siblings
        for sibling in graph["siblings"]:
            repo1 = sibling.get("repo1", "N/A")
            repo2 = sibling.get("repo2", "N/A")
            if repo1 != "N/A" and repo2 != "N/A":
                # Group siblings together
                # Find existing group that contains either repo
                group_found = False
                for group in sibling_groups:
                    if repo1 in group or repo2 in group:
                        group.add(repo1)
                        group.add(repo2)
                        group_found = True
                        break
                
                if not group_found:
                    # Create new group
                    sibling_groups.append({repo1, repo2})
        
        # Helper function to find which sibling group a repo belongs to
        def get_sibling_group(repo):
            for group in sibling_groups:
                if repo in group:
                    return group
            return None
        
        # Add rank constraints for repo sorting if enabled
        if sort_repos != "none" and sorted_repos:
            # Group repos by rank score, but merge siblings into same group
            rank_groups = {}
            repos_in_sibling_constraints = set()
            
            for repo, score in sorted_repos:
                if repo in graph["all_nodes"] and repo != graph["target"]:
                    # Check if this repo is in a sibling group
                    sibling_group = get_sibling_group(repo)
                    if sibling_group:
                        # Use a special key for siblings to group them together
                        # Use the first repo's score as the group key, or use a set ID
                        group_id = id(sibling_group)
                        score_key = f"sibling_{group_id}"
                        if score_key not in rank_groups:
                            rank_groups[score_key] = []
                        # Add all siblings to this group (including target if it's a sibling)
                        for sibling_repo in sibling_group:
                            if sibling_repo in graph["all_nodes"]:
                                if f'"{sibling_repo}"' not in rank_groups[score_key]:
                                    rank_groups[score_key].append(f'"{sibling_repo}"')
                                    repos_in_sibling_constraints.add(sibling_repo)
                    else:
                        # Not a sibling, use score-based grouping
                        if score not in rank_groups:
                            rank_groups[score] = []
                        if f'"{repo}"' not in rank_groups[score]:
                            rank_groups[score].append(f'"{repo}"')
            
            # Create rank constraints (highest scores at top if sort_repos == "top")
            if rank_groups:
                # Separate sibling groups from score-based groups
                sibling_group_keys = [k for k in rank_groups.keys() if k.startswith("sibling_")]
                score_keys = [k for k in rank_groups.keys() if not k.startswith("sibling_")]
                
                # Process sibling groups first (all at same level)
                for sibling_key in sibling_group_keys:
                    repo_list = rank_groups[sibling_key]
                    if len(repo_list) > 1:
                        dot_lines.append(f'  {{rank=same; {" ".join(repo_list)}}}')
                
                # Process score-based groups
                if score_keys:
                    # Convert score keys to numbers for sorting
                    score_nums = []
                    for k in score_keys:
                        try:
                            score_nums.append((int(k), k))
                        except (ValueError, TypeError):
                            score_nums.append((0, k))
                    
                    sorted_scores = sorted(score_nums, key=lambda x: x[0], reverse=(sort_repos == "top"))
                    for i, (score_val, score_key) in enumerate(sorted_scores):
                        if len(rank_groups[score_key]) > 0:
                            if sort_repos == "top" and i == 0:
                                rank_type = "min"
                            elif sort_repos == "bottom" and i == len(sorted_scores) - 1:
                                rank_type = "max"
                            else:
                                rank_type = "same"
                            dot_lines.append(f'  {{rank={rank_type}; {" ".join(rank_groups[score_key])}}}')
        else:
            # No sorting, just add sibling constraints (include target if it's a sibling)
            for group in sibling_groups:
                if len(group) > 1:
                    repo_list = [f'"{repo}"' for repo in group if repo in graph["all_nodes"]]
                    if len(repo_list) > 1:
                        dot_lines.append(f'  {{rank=same; {" ".join(repo_list)}}}')
        
        dot_lines.append("")
        
        # Track seen edges to avoid duplicates
        seen_edges = set()
        
        # Add children edges (dependencies) - deduplicated
        for child in graph["children"]:
            from_repo = child.get("from_repo", graph["target"])
            to_repo = child.get("to_repo", "N/A")
            if to_repo != "N/A":
                edge_key = (from_repo, to_repo, "uses")
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    dot_lines.append(f'  "{from_repo}" -> "{to_repo}" [label="uses", color=blue];')
        
        # Add parent edges (dependents) - deduplicated
        for parent in graph["parents"]:
            from_repo = parent.get("from_repo", "N/A")
            to_repo = parent.get("to_repo", graph["target"])
            if from_repo != "N/A":
                edge_key = (from_repo, to_repo, "depends on")
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    dot_lines.append(f'  "{from_repo}" -> "{to_repo}" [label="depends on", color=red];')
        
        # Add sibling edges (dashed lines, undirected, deduplicated)
        seen_sibling_pairs = set()
        for sibling in graph["siblings"]:
            repo1 = sibling.get("repo1", "N/A")
            repo2 = sibling.get("repo2", "N/A")
            if repo1 != "N/A" and repo2 != "N/A":
                # Use sorted tuple to ensure we only create one edge per sibling pair
                sibling_pair = tuple(sorted([repo1, repo2]))
                if sibling_pair not in seen_sibling_pairs:
                    seen_sibling_pairs.add(sibling_pair)
                    dot_lines.append(f'  "{repo1}" -> "{repo2}" [label="sibling", style=dashed, color=gray, dir=none];')
        
        # Add component relationships if enabled
        if show_components:
            # Contains relationships (repo -> component)
            for contains_rel in graph.get("contains", []):
                repo = contains_rel.get("from_repo", "N/A")
                comp = contains_rel.get("to_component", "N/A")
                if repo != "N/A" and comp != "N/A":
                    comp_id = comp.replace("-", "_").replace(" ", "_").replace(".", "_")
                    edge_key = (repo, comp_id, "contains")
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        dot_lines.append(f'  "{repo}" -> "{comp_id}" [label="contains", style=dotted, color=gray];')
            
            # Component dependencies (component -> component)
            for comp_dep in graph.get("component_depends", []):
                from_comp = comp_dep.get("from_component", "N/A")
                to_comp = comp_dep.get("to_component", "N/A")
                if from_comp != "N/A" and to_comp != "N/A":
                    from_id = from_comp.replace("-", "_").replace(" ", "_").replace(".", "_")
                    to_id = to_comp.replace("-", "_").replace(" ", "_").replace(".", "_")
                    edge_key = (from_id, to_id, "comp_depends")
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        dot_lines.append(f'  "{from_id}" -> "{to_id}" [label="depends", color=orange];')
            
            # Component to repo dependencies
            for comp_repo_dep in graph.get("component_depends_repo", []):
                comp = comp_repo_dep.get("from_component", "N/A")
                repo = comp_repo_dep.get("to_repo", "N/A")
                if comp != "N/A" and repo != "N/A":
                    comp_id = comp.replace("-", "_").replace(" ", "_").replace(".", "_")
                    edge_key = (comp_id, repo, "comp_depends_repo")
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        dot_lines.append(f'  "{comp_id}" -> "{repo}" [label="depends on repo", color=purple];')
        
        dot_lines.append("}")
        graph_output = "\n".join(dot_lines)
        
        if output:
            Path(output).write_text(graph_output)
            success(f"Graph written to: {output}")
        else:
            print(graph_output)
    
    elif format == "mermaid":
        # Generate Mermaid graph
        mermaid_lines = ["graph TB", ""]
        
        # Calculate repo ranks if sorting is enabled
        repo_ranks = {}
        if sort_repos != "none":
            repo_ranks = calculate_repo_ranks(graph, meta_repo_names)
        
        # Color mapping for Mermaid (hex colors)
        color_map = {
            "green": "#90EE90",
            "red": "#F08080",
            "blue": "#87CEEB",
            "yellow": "#FFFFE0",
            "orange": "#FFA07A",
            "purple": "#DDA0DD"
        }
        repo_fill_color = color_map.get(repo_color.lower(), repo_color)
        component_fill_color = color_map.get(component_color.lower(), component_color)
        
        # Define style classes
        mermaid_lines.append("  %% Style definitions")
        mermaid_lines.append(f'  classDef repoStyle fill:{repo_fill_color}')
        mermaid_lines.append(f'  classDef targetStyle fill:#87CEEB')
        mermaid_lines.append(f'  classDef componentStyle fill:{component_fill_color}')
        mermaid_lines.append("")
        
        # Add all repo nodes first (sorted if requested)
        seen_nodes = set()
        node_id_map = {}
        repos_to_add = sorted(graph["all_nodes"], key=lambda x: repo_ranks.get(x, 0), reverse=(sort_repos == "top")) if sort_repos != "none" else graph["all_nodes"]
        
        for node in repos_to_add:
            node_id = node.replace("-", "_")
            node_id_map[node] = node_id
            if node_id not in seen_nodes:
                seen_nodes.add(node_id)
                mermaid_lines.append(f'  {node_id}["{node}"]')
        
        # Add component nodes if enabled
        component_id_map = {}
        component_nodes_list = []
        if show_components and graph.get('component_nodes'):
            mermaid_lines.append("")
            mermaid_lines.append("  %% Component nodes")
            for comp in graph['component_nodes']:
                comp_id = comp.replace("-", "_").replace(" ", "_").replace(".", "_")
                component_id_map[comp] = comp_id
                if comp_id not in seen_nodes:
                    seen_nodes.add(comp_id)
                    mermaid_lines.append(f'  {comp_id}["{comp}"]')
                    component_nodes_list.append(comp_id)
        
        mermaid_lines.append("")
        
        # Track seen edges to avoid duplicates
        seen_edges = set()
        
        # Add children edges (dependencies) - deduplicated
        for child in graph["children"]:
            from_repo = child.get("from_repo", graph["target"])
            to_repo = child.get("to_repo", "N/A")
            if to_repo != "N/A" and to_repo in node_id_map:
                from_id = node_id_map.get(from_repo, from_repo.replace("-", "_"))
                to_id = node_id_map.get(to_repo, to_repo.replace("-", "_"))
                edge_key = (from_id, to_id, "uses")
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    mermaid_lines.append(f'  {from_id} -->|uses| {to_id}')
        
        # Add parent edges (dependents) - deduplicated
        for parent in graph["parents"]:
            from_repo = parent.get("from_repo", "N/A")
            to_repo = parent.get("to_repo", graph["target"])
            if from_repo != "N/A" and from_repo in node_id_map:
                from_id = node_id_map.get(from_repo, from_repo.replace("-", "_"))
                to_id = node_id_map.get(to_repo, to_repo.replace("-", "_"))
                edge_key = (from_id, to_id, "depends on")
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    mermaid_lines.append(f'  {from_id} -->|depends on| {to_id}')
        
        # Add sibling edges (undirected, deduplicated) - only one direction
        seen_sibling_pairs = set()
        for sibling in graph["siblings"]:
            repo1 = sibling.get("repo1", "N/A")
            repo2 = sibling.get("repo2", "N/A")
            if repo1 != "N/A" and repo2 != "N/A" and repo1 in node_id_map and repo2 in node_id_map:
                repo1_id = node_id_map.get(repo1, repo1.replace("-", "_"))
                repo2_id = node_id_map.get(repo2, repo2.replace("-", "_"))
                # Use sorted tuple to ensure we only create one edge per sibling pair
                sibling_pair = tuple(sorted([repo1_id, repo2_id]))
                if sibling_pair not in seen_sibling_pairs:
                    seen_sibling_pairs.add(sibling_pair)
                    mermaid_lines.append(f'  {repo1_id} -.->|sibling| {repo2_id}')
        
        # Add component relationships if enabled
        if show_components:
            # Contains relationships (repo -> component)
            for contains_rel in graph.get("contains", []):
                repo = contains_rel.get("from_repo", "N/A")
                comp = contains_rel.get("to_component", "N/A")
                if repo != "N/A" and comp != "N/A" and comp in component_id_map:
                    repo_id = node_id_map.get(repo, repo.replace("-", "_"))
                    comp_id = component_id_map[comp]
                    edge_key = (repo_id, comp_id, "contains")
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        mermaid_lines.append(f'  {repo_id} -->|contains| {comp_id}')
            
            # Component dependencies (component -> component)
            for comp_dep in graph.get("component_depends", []):
                from_comp = comp_dep.get("from_component", "N/A")
                to_comp = comp_dep.get("to_component", "N/A")
                if from_comp != "N/A" and to_comp != "N/A" and from_comp in component_id_map and to_comp in component_id_map:
                    from_id = component_id_map[from_comp]
                    to_id = component_id_map[to_comp]
                    edge_key = (from_id, to_id, "comp_depends")
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        mermaid_lines.append(f'  {from_id} -->|depends| {to_id}')
            
            # Component to repo dependencies
            for comp_repo_dep in graph.get("component_depends_repo", []):
                comp = comp_repo_dep.get("from_component", "N/A")
                repo = comp_repo_dep.get("to_repo", "N/A")
                if comp != "N/A" and repo != "N/A" and comp in component_id_map and repo in node_id_map:
                    comp_id = component_id_map[comp]
                    repo_id = node_id_map[repo]
                    edge_key = (comp_id, repo_id, "comp_depends_repo")
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        mermaid_lines.append(f'  {comp_id} -->|depends on repo| {repo_id}')
        
        # Apply styles using class statements
        mermaid_lines.append("")
        mermaid_lines.append("  %% Apply styles")
        for node in repos_to_add:
            node_id = node_id_map.get(node, node.replace("-", "_"))
            if node == graph["target"]:
                mermaid_lines.append(f'  class {node_id} targetStyle')
            elif node in meta_repo_names:
                mermaid_lines.append(f'  class {node_id} repoStyle')
        
        if show_components and component_nodes_list:
            for comp_id in component_nodes_list:
                mermaid_lines.append(f'  class {comp_id} componentStyle')
        
        graph_output = "\n".join(mermaid_lines)
        
        # Handle export if requested
        if export:
            if format != "mermaid":
                error("Export option only works with mermaid format. Use --format mermaid")
                raise typer.Exit(code=1)
            
            # Determine output path
            if output:
                export_path = Path(output)
            else:
                # Generate default filename
                export_ext = export.lower()
                if export_ext not in ("pdf", "png", "svg"):
                    error(f"Invalid export format: {export}. Use 'pdf', 'png', or 'svg'")
                    raise typer.Exit(code=1)
                export_path = Path(f"{graph['target']}_graph.{export_ext}")
            
            # Export to image
            if export_mermaid_to_image(graph_output, export_path, export, image_width, image_height):
                log(f"Mermaid diagram exported to: {export_path}")
            else:
                raise typer.Exit(code=1)
        elif output:
            Path(output).write_text(graph_output)
            success(f"Graph written to: {output}")
        else:
            print(graph_output)
    
    else:
        error(f"Unsupported format: {format}")
        raise typer.Exit(code=1)


@app.command(name="promotion-candidates")
def promotion_candidates(
    min_dependents: int = typer.Option(2, "--min-dependents", "-m", help="Minimum number of meta-repo dependents to be a candidate"),
    min_component_dependents: int = typer.Option(3, "--min-component-dependents", help="Minimum number of component dependents to be a candidate"),
    format: str = typer.Option("text", "--format", "-f", help="Output format (text, table)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file (JSON format)"),
):
    """Identify components that could be promoted to meta-repos based on dependency patterns."""
    # Find current meta-repo
    current_root = find_meta_repo_root()
    if not current_root:
        error("Could not find meta-repo root. Run from a meta-repo directory.")
        raise typer.Exit(code=1)
    
    workspace_root = current_root.parent
    
    # Scan all meta-repos in workspace
    meta_repo_names = ["meta-repo", "gambling-platform-meta", "scraping-platform-meta", "platform-meta"]
    all_meta_repos: Dict[str, Dict[str, Any]] = {}
    
    for repo_name_check in meta_repo_names:
        repo_path = workspace_root / repo_name_check
        if repo_path.exists() and (repo_path / "manifests" / "components.yaml").exists():
            try:
                components = get_components(str(repo_path / "manifests"))
                all_meta_repos[repo_name_check] = {
                    "path": repo_path,
                    "components": components
                }
            except Exception as e:
                log(f"Warning: Could not load {repo_name_check}: {e}")
    
    # Build component analysis
    component_analysis = {}  # component_name -> analysis data
    
    # Build component to repo map
    component_to_repo = {}
    component_data_map = {}
    for repo_name, repo_data in all_meta_repos.items():
        components = repo_data.get("components", {})
        for comp_name, comp_data in components.items():
            component_to_repo[comp_name] = repo_name
            component_data_map[comp_name] = comp_data
            component_analysis[comp_name] = {
                "name": comp_name,
                "current_repo": repo_name,
                "meta_repo_dependents": set(),  # Which meta-repos depend on this component
                "component_dependents": set(),  # Which components depend on this component
                "dependencies": set(comp_data.get("depends_on", [])),
                "dependency_count": len(comp_data.get("depends_on", [])),
            }
    
    # Analyze dependencies across all meta-repos
    for repo_name, repo_data in all_meta_repos.items():
        components = repo_data.get("components", {})
        for comp_name, comp_data in components.items():
            deps = comp_data.get("depends_on", [])
            for dep in deps:
                # Check if dependency is a component
                if dep in component_analysis:
                    component_analysis[dep]["component_dependents"].add(comp_name)
                    component_analysis[dep]["meta_repo_dependents"].add(repo_name)
                # Check if dependency is a meta-repo (component depends on entire meta-repo)
                elif dep in meta_repo_names:
                    # This component depends on a meta-repo, so components in that meta-repo
                    # could be considered as potential promotion candidates
                    pass
    
    # Calculate promotion scores
    candidates = []
    for comp_name, analysis in component_analysis.items():
        meta_repo_dep_count = len(analysis["meta_repo_dependents"])
        component_dep_count = len(analysis["component_dependents"])
        
        # Calculate promotion score
        # Higher score = better candidate
        score = (
            meta_repo_dep_count * 10 +  # Each meta-repo dependent is worth 10 points
            component_dep_count * 2 +    # Each component dependent is worth 2 points
            analysis["dependency_count"] * 1  # Having dependencies shows complexity
        )
        
        # Check if meets minimum thresholds
        is_candidate = (
            meta_repo_dep_count >= min_dependents or
            component_dep_count >= min_component_dependents
        )
        
        if is_candidate:
            candidates.append({
                "component": comp_name,
                "current_repo": analysis["current_repo"],
                "meta_repo_dependents": sorted(analysis["meta_repo_dependents"]),
                "meta_repo_dep_count": meta_repo_dep_count,
                "component_dependents": sorted(analysis["component_dependents"]),
                "component_dep_count": component_dep_count,
                "dependencies": sorted(analysis["dependencies"]),
                "dependency_count": analysis["dependency_count"],
                "promotion_score": score,
            })
    
    # Sort by promotion score (highest first)
    candidates.sort(key=lambda x: x["promotion_score"], reverse=True)
    
    # Display results
    if format == "text" or format == "table":
        panel("Component Promotion Candidates", "Meta-Repo Analysis")
        
        if not candidates:
            log(f"\nNo components meet the promotion criteria:")
            log(f"  - Minimum meta-repo dependents: {min_dependents}")
            log(f"  - Minimum component dependents: {min_component_dependents}")
            return
        
        log(f"\nFound {len(candidates)} promotion candidate(s):")
        log(f"  - Minimum meta-repo dependents: {min_dependents}")
        log(f"  - Minimum component dependents: {min_component_dependents}")
        
        rows = []
        for candidate in candidates:
            meta_repos_str = ", ".join(candidate["meta_repo_dependents"][:3])
            if len(candidate["meta_repo_dependents"]) > 3:
                meta_repos_str += f" (+{len(candidate['meta_repo_dependents']) - 3} more)"
            
            components_str = ", ".join(candidate["component_dependents"][:3])
            if len(candidate["component_dependents"]) > 3:
                components_str += f" (+{len(candidate['component_dependents']) - 3} more)"
            
            deps_str = ", ".join(candidate["dependencies"][:3])
            if len(candidate["dependencies"]) > 3:
                deps_str += f" (+{len(candidate['dependencies']) - 3} more)"
            
            rows.append([
                candidate["component"],
                candidate["current_repo"],
                str(candidate["meta_repo_dep_count"]),
                meta_repos_str or "None",
                str(candidate["component_dep_count"]),
                components_str or "None",
                str(candidate["dependency_count"]),
                deps_str or "None",
                str(candidate["promotion_score"])
            ])
        
        table(
            ["Component", "Current Repo", "Meta-Repo Deps", "Used By Meta-Repos", 
             "Component Deps", "Used By Components", "Has Deps", "Dependencies", "Score"],
            rows
        )
        
        # Provide recommendations
        log("\n💡 Recommendations:")
        for candidate in candidates[:5]:  # Top 5
            log(f"\n  📦 {candidate['component']} (Score: {candidate['promotion_score']})")
            log(f"     Currently in: {candidate['current_repo']}")
            if candidate["meta_repo_dep_count"] > 0:
                log(f"     ✅ Used by {candidate['meta_repo_dep_count']} meta-repo(s): {', '.join(candidate['meta_repo_dependents'])}")
            if candidate["component_dep_count"] > 0:
                log(f"     ✅ Used by {candidate['component_dep_count']} component(s)")
            if candidate["dependency_count"] > 0:
                log(f"     ✅ Has {candidate['dependency_count']} dependency/dependencies (shows complexity)")
            log(f"     💡 Consider promoting to: {candidate['component']}-meta")
        
        if output:
            import json
            Path(output).write_text(json.dumps(candidates, indent=2))
            success(f"Analysis written to: {output}")
    
    else:
        error(f"Unsupported format: {format}")
        raise typer.Exit(code=1)

