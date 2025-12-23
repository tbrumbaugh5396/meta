"""Component versioning strategy commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error
from meta.utils.versioning_strategies import get_versioning_manager, VersioningStrategy

app = typer.Typer(help="Component versioning strategies")


@app.command()
def bump(
    component: str = typer.Argument(..., help="Component name"),
    level: str = typer.Option("patch", "--level", "-l", help="Version level (major/minor/patch)"),
    strategy: VersioningStrategy = typer.Option("semantic", "--strategy", "-s", help="Versioning strategy"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Bump component version."""
    manager = get_versioning_manager()
    
    if manager.bump_version(component, level, strategy, manifests_dir):
        success(f"Version bumped for {component}")
    else:
        error("Failed to bump version")
        raise typer.Exit(code=1)


@app.command()
def generate(
    component: str = typer.Argument(..., help="Component name"),
    strategy: VersioningStrategy = typer.Option("semantic", "--strategy", "-s", help="Versioning strategy"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Generate new version using strategy."""
    from meta.utils.manifest import get_components
    
    manager = get_versioning_manager()
    
    components = get_components(manifests_dir)
    comp = components.get(component)
    current_version = comp.get("version") if comp else None
    
    new_version = manager.apply_strategy(component, strategy, current_version, manifests_dir)
    
    if new_version:
        log(f"Generated version: {new_version}")
    else:
        error("Failed to generate version")
        raise typer.Exit(code=1)

