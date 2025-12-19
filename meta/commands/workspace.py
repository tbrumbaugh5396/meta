"""Workspace management commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.workspace import get_workspace_manager

app = typer.Typer(help="Workspace management")


@app.command()
def create(
    name: str = typer.Argument(..., help="Workspace name"),
    manifests_dir: Optional[str] = typer.Option(None, "--manifests-dir", help="Manifests directory"),
):
    """Create a new workspace."""
    manager = get_workspace_manager()
    
    if manager.create_workspace(name, manifests_dir):
        success(f"Workspace {name} created")
    else:
        error("Failed to create workspace")
        raise typer.Exit(code=1)


@app.command()
def switch(
    name: str = typer.Argument(..., help="Workspace name"),
):
    """Switch to a workspace."""
    manager = get_workspace_manager()
    
    if manager.switch_workspace(name):
        success(f"Switched to workspace: {name}")
    else:
        error("Failed to switch workspace")
        raise typer.Exit(code=1)


@app.command()
def list():
    """List all workspaces."""
    manager = get_workspace_manager()
    workspaces = manager.list_workspaces()
    current = manager.get_current_workspace()
    
    if not workspaces:
        log("No workspaces found")
        return
    
    panel("Workspaces", "Workspace")
    rows = []
    for name, config in workspaces.items():
        marker = " (current)" if name == current else ""
        rows.append([
            name + marker,
            config.get("manifests_dir", "N/A"),
        ])
    
    table(["Name", "Manifests Dir"], rows)


@app.command()
def delete(
    name: str = typer.Argument(..., help="Workspace name"),
):
    """Delete a workspace."""
    manager = get_workspace_manager()
    
    if manager.delete_workspace(name):
        success(f"Workspace {name} deleted")
    else:
        error("Failed to delete workspace")
        raise typer.Exit(code=1)


@app.command()
def current():
    """Show current workspace."""
    manager = get_workspace_manager()
    current_ws = manager.get_current_workspace()
    
    if current_ws:
        log(f"Current workspace: {current_ws}")
    else:
        log("No workspace selected")


