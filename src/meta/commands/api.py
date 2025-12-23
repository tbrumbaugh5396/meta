"""API documentation commands."""

import typer
from pathlib import Path
from typing import Optional
from meta.utils.logger import log, success, error
from meta.utils.api_docs import generate_api_docs, extract_api_docs, validate_api
from meta.utils.manifest import get_components

app = typer.Typer(help="API documentation")


@app.command()
def docs(
    component: str = typer.Argument(..., help="Component name"),
    format: str = typer.Option("markdown", "--format", "-f", help="Output format (markdown/html)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Generate API documentation for a component."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = Path(f"components/{component}")
    
    if not component_path.exists():
        error(f"Component directory not found: {component_path}")
        raise typer.Exit(code=1)
    
    docs = generate_api_docs(component, component_path, format)
    
    if output:
        Path(output).write_text(docs)
        success(f"API documentation written to: {output}")
    else:
        print(docs)


@app.command()
def validate(
    component: str = typer.Argument(..., help="Component name"),
):
    """Validate API consistency."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = Path(f"components/{component}")
    
    if validate_api(component, component_path):
        success(f"API validation passed for {component}")
    else:
        error("API validation failed")
        raise typer.Exit(code=1)


@app.command()
def test(
    component: str = typer.Argument(..., help="Component name"),
):
    """Test API endpoints."""
    log(f"Testing API for {component}")
    log("API testing not fully implemented")
    log("Use API testing tools like Postman, curl, or httpx")


