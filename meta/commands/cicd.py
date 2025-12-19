"""CI/CD template commands."""

import typer
from pathlib import Path
from typing import Optional
from meta.utils.logger import log, success, error
from meta.utils.cicd_templates import scaffold_cicd, validate_cicd, generate_cicd_template
from meta.utils.manifest import get_components

app = typer.Typer(help="CI/CD template management")


@app.command()
def scaffold(
    component: str = typer.Argument(..., help="Component name"),
    provider: str = typer.Argument(..., help="CI/CD provider (github/gitlab/jenkins)"),
):
    """Scaffold CI/CD configuration for a component."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = Path(f"components/{component}")
    
    if not component_path.exists():
        error(f"Component directory not found: {component_path}")
        raise typer.Exit(code=1)
    
    if scaffold_cicd(component, provider, component_path):
        success(f"Scaffolded CI/CD config for {component}")
    else:
        error("Failed to scaffold CI/CD config")
        raise typer.Exit(code=1)


@app.command()
def validate(
    component: str = typer.Argument(..., help="Component name"),
):
    """Validate CI/CD configuration."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = Path(f"components/{component}")
    
    if validate_cicd(component, component_path):
        success(f"CI/CD configuration valid for {component}")
    else:
        error("CI/CD configuration not found or invalid")
        raise typer.Exit(code=1)


@app.command()
def test(
    component: str = typer.Argument(..., help="Component name"),
):
    """Test CI/CD pipeline locally."""
    log(f"Testing CI/CD pipeline for {component}")
    log("Local CI/CD testing not fully implemented")
    log("Use the provider's local testing tools (e.g., act for GitHub Actions)")


