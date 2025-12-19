"""Dependency graph visualization commands."""

import typer
from pathlib import Path
from typing import Optional
from meta.utils.logger import log, success, error
from meta.utils.visualization import generate_dot_graph, generate_mermaid_graph, generate_text_tree
from meta.utils.manifest import get_components

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


