"""Changelog management commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error
from meta.utils.changelog import generate_changelog_entry, update_changelog, get_commits_since
from meta.utils.manifest import get_components

app = typer.Typer(help="Manage component changelogs")


@app.command()
def generate(
    component: str = typer.Argument(..., help="Component name"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Version for changelog entry"),
    since: Optional[str] = typer.Option(None, "--since", help="Since version or date"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Generate changelog entry."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = f"components/{component}"
    comp_path = Path(component_path)
    
    if not comp_path.exists():
        error(f"Component directory not found: {component_path}")
        raise typer.Exit(code=1)
    
    if version is None:
        # Get current version or generate next
        from meta.utils.git import get_current_version
        current = get_current_version(component_path)
        if current:
            version = current
        else:
            version = "v0.1.0"
    
    log(f"Generating changelog for {component} version {version}")
    
    entry = generate_changelog_entry(component, version, component_path, since)
    
    if output:
        Path(output).write_text(entry)
        success(f"Changelog written to: {output}")
    else:
        print(entry)


@app.command()
def update(
    component: str = typer.Argument(..., help="Component name"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Version for changelog entry"),
    since: Optional[str] = typer.Option(None, "--since", help="Since version or date"),
    changelog_path: Optional[str] = typer.Option(None, "--changelog", help="Changelog file path"),
):
    """Update changelog file."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = f"components/{component}"
    comp_path = Path(component_path)
    
    if not comp_path.exists():
        error(f"Component directory not found: {component_path}")
        raise typer.Exit(code=1)
    
    if version is None:
        from meta.utils.git import get_current_version
        current = get_current_version(component_path)
        if current:
            version = current
        else:
            version = "v0.1.0"
    
    if update_changelog(component, version, component_path, changelog_path, since):
        success(f"Updated changelog for {component}")
    else:
        error("Failed to update changelog")
        raise typer.Exit(code=1)


@app.command()
def release(
    component: str = typer.Argument(..., help="Component name"),
    version: str = typer.Argument(..., help="Release version"),
    since: Optional[str] = typer.Option(None, "--since", help="Since version or date"),
):
    """Generate release changelog."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = f"components/{component}"
    
    log(f"Generating release changelog for {component} {version}")
    
    entry = generate_changelog_entry(component, version, component_path, since)
    
    # Also update changelog file
    update_changelog(component, version, component_path, since=since)
    
    print(entry)
    success(f"Release changelog generated for {component} {version}")


