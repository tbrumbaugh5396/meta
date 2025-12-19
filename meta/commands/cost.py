"""Cost tracking commands."""

import typer
from pathlib import Path
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.cost_tracking import track_resource_usage, estimate_cost, optimize_costs
from meta.utils.manifest import get_components

app = typer.Typer(help="Cost tracking")


@app.command()
def track(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Component name"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Track all components"),
):
    """Track resource usage and costs."""
    components = get_components()
    
    if component:
        if component not in components:
            error(f"Component {component} not found")
            raise typer.Exit(code=1)
        
        component_path = Path(f"components/{component}")
        usage = track_resource_usage(component, component_path)
        
        panel(f"Resource Usage: {component}", "Cost")
        rows = [
            ["CPU Hours", f"{usage['cpu_hours']:.2f}"],
            ["Memory GB Hours", f"{usage['memory_gb_hours']:.2f}"],
            ["Storage GB", f"{usage['storage_gb']:.2f}"],
            ["Network GB", f"{usage['network_gb']:.2f}"],
            ["Estimated Cost", f"${usage['estimated_cost']:.2f}"],
        ]
        table(["Resource", "Usage"], rows)
    
    elif all_components:
        all_usage = []
        for comp_name in components.keys():
            comp_path = Path(f"components/{comp_name}")
            if comp_path.exists():
                usage = track_resource_usage(comp_name, comp_path)
                all_usage.append(usage)
        
        panel(f"Resource Usage: {len(all_usage)} component(s)", "Cost")
        total_cost = sum(u["estimated_cost"] for u in all_usage)
        log(f"Total estimated cost: ${total_cost:.2f}")


@app.command()
def estimate(
    component: str = typer.Argument(..., help="Component name"),
    period_days: int = typer.Option(30, "--period", "-p", help="Period in days"),
):
    """Estimate cost for a component."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = Path(f"components/{component}")
    
    estimate_data = estimate_cost(component, component_path, period_days)
    
    panel(f"Cost Estimate: {component}", "Cost")
    log(f"Period: {period_days} days")
    log(f"Estimated cost: ${estimate_data['estimated_cost']:.2f}")


@app.command()
def optimize(
    component: str = typer.Argument(..., help="Component name"),
):
    """Get cost optimization suggestions."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = Path(f"components/{component}")
    
    suggestions = optimize_costs(component, component_path)
    
    panel(f"Cost Optimization: {component}", "Cost")
    for suggestion in suggestions:
        log(f"  - {suggestion}")


