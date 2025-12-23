"""Dependency injection commands."""

import typer
from pathlib import Path
from typing import Optional
from meta.utils.logger import log, success, error
from meta.utils.dependency_injection import discover_services, inject_dependency, validate_dependencies
from meta.utils.manifest import get_components

app = typer.Typer(help="Dependency injection")


@app.command()
def discover(
    component: str = typer.Argument(..., help="Component name"),
):
    """Discover services in a component."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = Path(f"components/{component}")
    
    services = discover_services(component, component_path)
    
    if services:
        log(f"Found {len(services)} service(s) in {component}")
        for service in services:
            log(f"  - {service.get('name', 'unknown')}")
    else:
        log(f"No services found in {component}")


@app.command()
def inject(
    component: str = typer.Argument(..., help="Component name"),
    dependency: str = typer.Argument(..., help="Dependency to inject"),
):
    """Inject a dependency into a component."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = Path(f"components/{component}")
    
    if inject_dependency(component, dependency, component_path):
        success(f"Injected {dependency} into {component}")
    else:
        error("Failed to inject dependency")
        raise typer.Exit(code=1)


@app.command()
def validate(
    component: str = typer.Argument(..., help="Component name"),
):
    """Validate component dependencies."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = Path(f"components/{component}")
    
    if validate_dependencies(component, component_path):
        success(f"Dependencies validated for {component}")
    else:
        error("Dependency validation failed")
        raise typer.Exit(code=1)


