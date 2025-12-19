"""Component registry commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.registry import get_registry

app = typer.Typer(help="Component registry")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    registry_url: Optional[str] = typer.Option(None, "--registry-url", help="Registry URL"),
):
    """Search for components in registry."""
    registry = get_registry(registry_url)
    
    log(f"Searching for: {query}")
    results = registry.search(query)
    
    if not results:
        log("No components found")
        return
    
    panel(f"Search Results: {len(results)} component(s)", "Registry")
    rows = []
    for comp in results:
        rows.append([
            comp.get("name", "unknown"),
            comp.get("version", "N/A"),
            comp.get("description", "No description")[:50]
        ])
    
    table(["Name", "Version", "Description"], rows)


@app.command()
def publish(
    component_name: str = typer.Argument(..., help="Component name"),
    registry_url: Optional[str] = typer.Option(None, "--registry-url", help="Registry URL"),
    repo: Optional[str] = typer.Option(None, "--repo", help="Repository URL"),
    version: Optional[str] = typer.Option(None, "--version", help="Version"),
    description: Optional[str] = typer.Option(None, "--description", help="Description"),
):
    """Publish component to registry."""
    registry = get_registry(registry_url)
    
    metadata = {}
    if repo:
        metadata["repo"] = repo
    if version:
        metadata["version"] = version
    if description:
        metadata["description"] = description
    
    if registry.publish(component_name, metadata):
        success(f"Published {component_name} to registry")
    else:
        error("Failed to publish component")
        raise typer.Exit(code=1)


@app.command()
def install(
    component_name: str = typer.Argument(..., help="Component name"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Version to install"),
    target_dir: str = typer.Option("components", "--target-dir", help="Target directory"),
    registry_url: Optional[str] = typer.Option(None, "--registry-url", help="Registry URL"),
):
    """Install component from registry."""
    registry = get_registry(registry_url)
    
    if registry.install(component_name, version, target_dir):
        success(f"Installed {component_name}")
    else:
        error("Failed to install component")
        raise typer.Exit(code=1)


@app.command()
def info(
    component_name: str = typer.Argument(..., help="Component name"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Version"),
    registry_url: Optional[str] = typer.Option(None, "--registry-url", help="Registry URL"),
):
    """Show component information from registry."""
    registry = get_registry(registry_url)
    
    comp_info = registry.get_component(component_name, version)
    
    if not comp_info:
        error(f"Component {component_name} not found")
        raise typer.Exit(code=1)
    
    panel(f"Component: {component_name}", "Registry")
    from meta.utils.logger import table
    rows = [
        ["Name", comp_info.get("name", "N/A")],
        ["Version", comp_info.get("version", "N/A")],
        ["Repository", comp_info.get("repo", "N/A")],
        ["Description", comp_info.get("description", "N/A")],
    ]
    table(["Property", "Value"], rows)


