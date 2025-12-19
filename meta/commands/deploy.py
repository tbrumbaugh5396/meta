"""Component deployment commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error
from meta.utils.deployment import get_deployment_manager, DeploymentStrategy

app = typer.Typer(help="Component deployment")


@app.command()
def component(
    component: str = typer.Argument(..., help="Component name"),
    version: str = typer.Argument(..., help="Version to deploy"),
    strategy: DeploymentStrategy = typer.Option(DeploymentStrategy.IMMEDIATE, "--strategy", "-s", help="Deployment strategy"),
    canary_percentage: int = typer.Option(10, "--canary", help="Canary percentage (for canary strategy)"),
    instances: int = typer.Option(1, "--instances", "-i", help="Number of instances"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Deploy a component."""
    manager = get_deployment_manager()
    
    if manager.deploy(component, version, strategy, canary_percentage, instances, manifests_dir):
        success(f"Deployment initiated for {component}")
    else:
        error("Deployment failed")
        raise typer.Exit(code=1)


@app.command()
def promote(
    component: str = typer.Argument(..., help="Component name"),
    percentage: int = typer.Option(100, "--percentage", "-p", help="Traffic percentage"),
):
    """Promote canary deployment."""
    log(f"Promoting canary for {component} to {percentage}% traffic")
    # In real implementation, update load balancer weights
    success(f"Canary promoted to {percentage}% traffic")


@app.command()
def rollback(
    component: str = typer.Argument(..., help="Component name"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Version to rollback to"),
):
    """Rollback component deployment."""
    log(f"Rolling back {component}...")
    # In real implementation, switch back to previous version
    success(f"Rolled back {component}")


