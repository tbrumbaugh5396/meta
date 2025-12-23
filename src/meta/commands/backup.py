"""Backup and restore commands."""

import typer
from typing import Optional, List
from meta.utils.logger import log, success, error
from meta.utils.backup import create_backup, restore_backup

app = typer.Typer(help="Backup and restore meta-repo state")


@app.command()
def create(
    output: str = typer.Option("backup.tar.gz", "--output", "-o", help="Output backup file"),
    components: Optional[str] = typer.Option(None, "--components", help="Comma-separated component list"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    include_store: bool = typer.Option(False, "--include-store", help="Include store in backup"),
    include_cache: bool = typer.Option(False, "--include-cache", help="Include cache in backup"),
):
    """Create a backup of meta-repo state."""
    comp_list = None
    if components:
        comp_list = [c.strip() for c in components.split(",")]
    
    if create_backup(output, comp_list, manifests_dir, include_store, include_cache):
        success(f"Backup created: {output}")
    else:
        error("Failed to create backup")
        raise typer.Exit(code=1)


@app.command()
def restore(
    backup_file: str = typer.Argument(..., help="Backup file to restore from"),
    components: Optional[str] = typer.Option(None, "--components", help="Comma-separated component list"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    restore_store: bool = typer.Option(False, "--restore-store", help="Restore store from backup"),
    restore_cache: bool = typer.Option(False, "--restore-cache", help="Restore cache from backup"),
):
    """Restore from a backup."""
    comp_list = None
    if components:
        comp_list = [c.strip() for c in components.split(",")]
    
    if restore_backup(backup_file, comp_list, manifests_dir, restore_store, restore_cache):
        success(f"Backup restored from: {backup_file}")
    else:
        error("Failed to restore backup")
        raise typer.Exit(code=1)


