"""Component sync commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table
from meta.utils.sync import sync_component, sync_all_components, sync_environment

app = typer.Typer(help="Component synchronization")


@app.command()
def component(
    component: str = typer.Argument(..., help="Component name"),
    env: str = typer.Option("dev", "--env", "-e", help="Environment"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Sync a component to desired version."""
    if sync_component(component, env, manifests_dir):
        success(f"Synced {component}")
    else:
        error("Sync failed")
        raise typer.Exit(code=1)


@app.command()
def all(
    env: str = typer.Option("dev", "--env", "-e", help="Environment"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Sync all components."""
    results = sync_all_components(env, manifests_dir)
    
    rows = []
    for component, success_flag in results.items():
        status = "✓" if success_flag else "✗"
        rows.append([status, component])
    
    table(["Status", "Component"], rows)
    
    failed = [c for c, s in results.items() if not s]
    if failed:
        error(f"Failed to sync: {', '.join(failed)}")
        raise typer.Exit(code=1)
    else:
        success("All components synced")


@app.command()
def env(
    env: str = typer.Argument(..., help="Environment name"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Sync all components in an environment."""
    results = sync_environment(env, manifests_dir)
    
    rows = []
    for component, success_flag in results.items():
        status = "✓" if success_flag else "✗"
        rows.append([status, component])
    
    table(["Status", "Component"], rows)
    
    failed = [c for c, s in results.items() if not s]
    if failed:
        error(f"Failed to sync: {', '.join(failed)}")
        raise typer.Exit(code=1)
    else:
        success(f"Environment {env} synced")


