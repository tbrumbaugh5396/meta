"""Component publishing commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error
from meta.utils.publish import publish_component, bump_version

app = typer.Typer(help="Publish components")


@app.command()
def component(
    component_name: str = typer.Argument(..., help="Component name"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Version to publish"),
    bump: Optional[str] = typer.Option(None, "--bump", help="Bump type (major, minor, patch)"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    no_tag: bool = typer.Option(False, "--no-tag", help="Don't create git tag"),
    no_manifest: bool = typer.Option(False, "--no-manifest", help="Don't update manifest"),
):
    """Publish a component."""
    if version and bump:
        error("Specify either --version or --bump, not both")
        raise typer.Exit(code=1)
    
    bump_type = bump or "patch"
    
    if publish_component(component_name, version, bump_type, manifests_dir,
                        create_tag_flag=not no_tag, update_manifest=not no_manifest):
        success(f"Published {component_name}")
    else:
        error("Failed to publish component")
        raise typer.Exit(code=1)


