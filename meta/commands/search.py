"""Enhanced component search commands."""

import typer
from typing import Optional
from meta.utils.logger import log, table
from meta.utils.search import search_components, search_by_dependency, search_by_version

app = typer.Typer(help="Enhanced component search")


@app.command()
def components(
    query: str = typer.Argument(..., help="Search query"),
    search_type: str = typer.Option("all", "--type", "-t", help="Search type (name/type/repo/tag/all)"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Search components."""
    results = search_components(query, search_type, manifests_dir)
    
    if not results:
        log(f"No components found matching: {query}")
        return
    
    rows = []
    for result in results:
        matches_str = ", ".join(result.get("matches", []))
        rows.append([
            result["name"],
            result["type"],
            result["version"],
            result.get("current_version", "unknown"),
            matches_str
        ])
    
    table(["Name", "Type", "Desired Version", "Current Version", "Matches"], rows)


@app.command()
def deps(
    component: str = typer.Argument(..., help="Component name"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Find components that depend on a component."""
    dependents = search_by_dependency(component, manifests_dir)
    
    if not dependents:
        log(f"No components depend on: {component}")
        return
    
    rows = [[dep] for dep in dependents]
    table(["Dependent Components"], rows)


@app.command()
def version(
    pattern: str = typer.Argument(..., help="Version pattern (regex)"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Search components by version pattern."""
    results = search_by_version(pattern, manifests_dir)
    
    if not results:
        log(f"No components found with version matching: {pattern}")
        return
    
    rows = []
    for result in results:
        rows.append([result["name"], result["version"], result["type"]])
    
    table(["Name", "Version", "Type"], rows)


