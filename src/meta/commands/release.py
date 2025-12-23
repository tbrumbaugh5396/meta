"""Release automation commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error
from meta.utils.release import prepare_release, publish_release, rollback_release
from meta.utils.manifest import get_components

app = typer.Typer(help="Component release automation")


@app.command()
def prepare(
    component: str = typer.Argument(..., help="Component name"),
    version: str = typer.Argument(..., help="Release version"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    no_validate: bool = typer.Option(False, "--no-validate", help="Skip validation"),
    no_changelog: bool = typer.Option(False, "--no-changelog", help="Skip changelog update"),
):
    """Prepare a component release."""
    if prepare_release(component, version, manifests_dir,
                      validate=not no_validate,
                      update_changelog_flag=not no_changelog):
        success(f"Release prepared for {component} version {version}")
    else:
        error("Failed to prepare release")
        raise typer.Exit(code=1)


@app.command()
def publish(
    component: str = typer.Argument(..., help="Component name"),
    version: str = typer.Argument(..., help="Release version"),
    no_tag: bool = typer.Option(False, "--no-tag", help="Don't create git tag"),
    no_push: bool = typer.Option(False, "--no-push", help="Don't push tag"),
):
    """Publish a component release."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = f"components/{component}"
    
    if publish_release(component, version, component_path,
                      create_tag_flag=not no_tag,
                      push=not no_push):
        success(f"Published release for {component} version {version}")
    else:
        error("Failed to publish release")
        raise typer.Exit(code=1)


@app.command()
def rollback(
    component: str = typer.Argument(..., help="Component name"),
    from_version: str = typer.Argument(..., help="Version to rollback from"),
):
    """Rollback a component release."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = f"components/{component}"
    
    if rollback_release(component, from_version, component_path):
        success(f"Rolled back {component} from {from_version}")
    else:
        error("Failed to rollback release")
        raise typer.Exit(code=1)


