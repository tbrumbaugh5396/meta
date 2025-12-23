"""Component alias commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table
from meta.utils.aliases import create_alias, delete_alias, list_aliases, resolve_alias

app = typer.Typer(help="Component aliases")


@app.command()
def create(
    alias_type: str = typer.Argument(..., help="Alias type (comp/env)"),
    alias: str = typer.Argument(..., help="Alias name"),
    target: str = typer.Argument(..., help="Target value"),
):
    """Create an alias."""
    if create_alias(alias_type, alias, target):
        success(f"Created alias: {alias_type}:{alias} -> {target}")
    else:
        error("Failed to create alias")
        raise typer.Exit(code=1)


@app.command()
def delete(
    alias_type: str = typer.Argument(..., help="Alias type (comp/env)"),
    alias: str = typer.Argument(..., help="Alias name"),
):
    """Delete an alias."""
    if delete_alias(alias_type, alias):
        success(f"Deleted alias: {alias_type}:{alias}")
    else:
        error("Alias not found")
        raise typer.Exit(code=1)


@app.command()
def list(
    alias_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by type"),
):
    """List aliases."""
    aliases = list_aliases(alias_type)
    
    if not aliases:
        log("No aliases defined")
        return
    
    rows = []
    for alias, target in aliases.items():
        rows.append([alias, target])
    
    table(["Alias", "Target"], rows)


@app.command()
def resolve(
    alias_type: str = typer.Argument(..., help="Alias type (comp/env)"),
    alias: str = typer.Argument(..., help="Alias name"),
):
    """Resolve an alias."""
    target = resolve_alias(alias_type, alias)
    
    if target:
        log(f"{alias_type}:{alias} -> {target}")
    else:
        error("Alias not found")
        raise typer.Exit(code=1)


