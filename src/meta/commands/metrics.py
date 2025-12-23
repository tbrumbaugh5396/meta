"""Performance metrics commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.metrics import get_metrics_collector

app = typer.Typer(help="Performance metrics")


@app.command()
def component(
    component_name: str = typer.Argument(..., help="Component name"),
    days: int = typer.Option(7, "--days", "-d", help="Number of days to look back"),
):
    """Show metrics for a specific component."""
    collector = get_metrics_collector()
    metrics = collector.get_component_metrics(component_name, days)
    
    if not metrics:
        log(f"No metrics found for {component_name}")
        return
    
    panel(f"Metrics: {component_name} (last {days} days)", "Metrics")
    rows = [
        ["Total Operations", metrics.get("total_operations", 0)],
        ["Successful", metrics.get("successful", 0)],
        ["Failed", metrics.get("failed", 0)],
        ["Avg Duration", f"{metrics.get('avg_duration', 0.0):.2f}s"],
        ["Min Duration", f"{metrics.get('min_duration', 0.0):.2f}s"],
        ["Max Duration", f"{metrics.get('max_duration', 0.0):.2f}s"],
    ]
    table(["Metric", "Value"], rows)


@app.command()
def all(
    days: int = typer.Option(7, "--days", "-d", help="Number of days to look back"),
    export: Optional[str] = typer.Option(None, "--export", help="Export to file (json)"),
):
    """Show all metrics."""
    collector = get_metrics_collector()
    metrics = collector.get_all_metrics(days)
    
    if not metrics or metrics.get("total_operations", 0) == 0:
        log("No metrics found")
        return
    
    panel(f"All Metrics (last {days} days)", "Metrics")
    rows = [
        ["Total Operations", metrics.get("total_operations", 0)],
        ["Successful", metrics.get("successful", 0)],
        ["Failed", metrics.get("failed", 0)],
        ["Avg Duration", f"{metrics.get('avg_duration', 0.0):.2f}s"],
    ]
    table(["Metric", "Value"], rows)
    
    # Show by component
    by_component = metrics.get("by_component", {})
    if by_component:
        log("\nBy Component:")
        comp_rows = []
        for comp, stats in sorted(by_component.items(), key=lambda x: x[1]["operations"], reverse=True):
            comp_rows.append([
                comp,
                stats["operations"],
                f"{stats['avg_duration']:.2f}s"
            ])
        table(["Component", "Operations", "Avg Duration"], comp_rows)
    
    # Export if requested
    if export:
        import json
        with open(export, 'w') as f:
            json.dump(metrics, f, indent=2)
        success(f"Metrics exported to: {export}")


