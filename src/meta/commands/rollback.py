"""Rollback commands for reverting to previous states."""

import typer
from typing import Optional, List
from pathlib import Path
from meta.utils.logger import log, success, error, table, panel
from meta.utils.rollback import (
    find_rollback_targets,
    rollback_component,
    rollback_from_lock_file,
    rollback_from_store,
    create_rollback_snapshot,
    RollbackTarget
)

app = typer.Typer(help="Rollback components to previous states")


@app.command()
def component(
    component: str = typer.Argument(..., help="Component name"),
    to_version: Optional[str] = typer.Option(None, "--to-version", "-v", help="Version to rollback to"),
    to_commit: Optional[str] = typer.Option(None, "--to-commit", "-c", help="Commit SHA to rollback to"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Rollback a specific component to a previous version or commit."""
    if not to_version and not to_commit:
        error("Specify either --to-version or --to-commit")
        raise typer.Exit(code=1)
    
    target = RollbackTarget(
        component=component,
        version=to_version,
        commit=to_commit
    )
    
    if rollback_component(component, target, manifests_dir):
        success(f"Rolled back {component}")
    else:
        error(f"Failed to rollback {component}")
        raise typer.Exit(code=1)


@app.command()
def lock(
    lock_file: str = typer.Argument(..., help="Lock file to rollback to"),
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Rollback specific component only"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Rollback components to versions specified in a lock file."""
    if not Path(lock_file).exists():
        error(f"Lock file not found: {lock_file}")
        raise typer.Exit(code=1)
    
    if rollback_from_lock_file(lock_file, component, manifests_dir):
        success("Rollback from lock file completed")
    else:
        error("Rollback failed")
        raise typer.Exit(code=1)


@app.command()
def store(
    component: str = typer.Argument(..., help="Component name"),
    content_hash: str = typer.Argument(..., help="Content hash from store"),
    store_dir: str = typer.Option(".meta-store", "--store-dir", help="Store directory"),
):
    """Rollback component from content-addressed store."""
    if rollback_from_store(component, content_hash, store_dir):
        success(f"Rolled back {component} from store")
    else:
        error("Rollback from store failed")
        raise typer.Exit(code=1)


@app.command()
def list(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="List targets for specific component"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """List available rollback targets."""
    targets = find_rollback_targets(component, manifests_dir)
    
    if not targets:
        log("No rollback targets found")
        return
    
    panel("Available Rollback Targets", "Rollback")
    rows = []
    for target in targets:
        ref = target.commit[:8] if target.commit else target.version or "unknown"
        rows.append([
            target.component,
            ref,
            target.lock_file or "current"
        ])
    
    table(["Component", "Target", "Source"], rows)


@app.command()
def snapshot(
    components: Optional[str] = typer.Option(None, "--components", help="Comma-separated component list"),
    output: str = typer.Option("rollback-snapshot.yaml", "--output", "-o", help="Snapshot file path"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Create a snapshot of current state for rollback."""
    comp_list = None
    if components:
        comp_list = [c.strip() for c in components.split(",")]
    
    if create_rollback_snapshot(comp_list, manifests_dir, output):
        success(f"Snapshot created: {output}")
    else:
        error("Failed to create snapshot")
        raise typer.Exit(code=1)


