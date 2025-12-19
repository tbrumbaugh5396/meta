"""Documentation generation commands."""

import typer
from pathlib import Path
from typing import Optional
from meta.utils.logger import log, success, error
from meta.utils.docs import generate_component_docs, generate_readme, generate_api_docs
from meta.utils.manifest import get_components

app = typer.Typer(help="Generate component documentation")


@app.command()
def generate(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Component name"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Generate for all components"),
    format: str = typer.Option("markdown", "--format", "-f", help="Output format (markdown/html)"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
):
    """Generate documentation for components."""
    if component:
        if generate_component_docs(component, format, output_dir):
            success(f"Generated documentation for {component}")
        else:
            error("Failed to generate documentation")
            raise typer.Exit(code=1)
    elif all_components:
        components = get_components()
        success_count = 0
        for comp_name in components.keys():
            if generate_component_docs(comp_name, format, output_dir):
                success_count += 1
        
        success(f"Generated documentation for {success_count}/{len(components)} components")
    else:
        error("Specify --component or --all")
        raise typer.Exit(code=1)


@app.command()
def serve(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Component name"),
    port: int = typer.Option(8000, "--port", "-p", help="Server port"),
):
    """Serve documentation locally."""
    log(f"Starting documentation server on port {port}")
    log("Documentation server not fully implemented - use a static file server")
    log(f"Would serve docs from: docs/{component or 'all'}")


