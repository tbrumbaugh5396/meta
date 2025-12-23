"""Component templates library commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.templates_library import get_template_library

app = typer.Typer(help="Component templates library")


@app.command()
def list(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
):
    """List available templates."""
    library = get_template_library()
    templates = library.list_templates(category)
    
    if not templates:
        log("No templates available")
        return
    
    panel(f"Templates: {len(templates)} template(s)", "Templates")
    rows = []
    for template in templates:
        rows.append([
            template.get("name", "unknown"),
            template.get("category", "general"),
            template.get("description", "No description")[:50]
        ])
    
    table(["Name", "Category", "Description"], rows)


@app.command()
def install(
    name: str = typer.Argument(..., help="Template name"),
    source: str = typer.Argument(..., help="Template source path or URL"),
    category: str = typer.Option("general", "--category", "-c", help="Template category"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Template description"),
):
    """Install a template."""
    library = get_template_library()
    
    if library.install_template(name, source, category, description):
        success(f"Installed template: {name}")
    else:
        error("Failed to install template")
        raise typer.Exit(code=1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
):
    """Search for templates."""
    library = get_template_library()
    results = library.search_templates(query)
    
    if not results:
        log(f"No templates found matching: {query}")
        return
    
    panel(f"Search Results: {len(results)} template(s)", "Templates")
    rows = []
    for template in results:
        rows.append([
            template.get("name", "unknown"),
            template.get("category", "general"),
            template.get("description", "No description")[:50]
        ])
    
    table(["Name", "Category", "Description"], rows)


@app.command()
def publish(
    name: str = typer.Argument(..., help="Template name"),
    registry_url: Optional[str] = typer.Option(None, "--registry", help="Registry URL"),
):
    """Publish template to registry."""
    library = get_template_library()
    
    if library.publish_template(name, registry_url):
        success(f"Published template: {name}")
    else:
        error("Failed to publish template")
        raise typer.Exit(code=1)


