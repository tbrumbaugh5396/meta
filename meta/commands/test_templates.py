"""Test template commands."""

import typer
from pathlib import Path
from typing import Optional
from meta.utils.logger import log, success, error
from meta.utils.test_templates import scaffold_test, get_test_coverage
from meta.utils.manifest import get_components

app = typer.Typer(help="Test template management")


@app.command()
def scaffold(
    component: str = typer.Argument(..., help="Component name"),
    test_type: str = typer.Argument(..., help="Test type (unit/integration/e2e)"),
):
    """Scaffold test files for a component."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = Path(f"components/{component}")
    
    if not component_path.exists():
        error(f"Component directory not found: {component_path}")
        raise typer.Exit(code=1)
    
    if scaffold_test(component, test_type, component_path):
        success(f"Scaffolded {test_type} tests for {component}")
    else:
        error("Failed to scaffold tests")
        raise typer.Exit(code=1)


@app.command()
def coverage(
    component: str = typer.Argument(..., help="Component name"),
    threshold: Optional[float] = typer.Option(None, "--threshold", help="Coverage threshold"),
):
    """Get test coverage for a component."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = Path(f"components/{component}")
    
    coverage = get_test_coverage(component, component_path)
    if coverage is not None:
        log(f"Test coverage: {coverage:.1f}%")
        if threshold and coverage < threshold:
            error(f"Coverage {coverage:.1f}% below threshold {threshold}%")
            raise typer.Exit(code=1)
    else:
        log("Coverage information not available")


