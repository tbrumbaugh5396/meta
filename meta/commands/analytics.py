"""Component analytics commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.analytics import (
    get_usage_statistics, get_performance_trends,
    get_dependency_analysis, get_health_trends
)

app = typer.Typer(help="Component analytics")


@app.command()
def usage(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Component name"),
    days: int = typer.Option(30, "--days", "-d", help="Number of days"),
):
    """Show usage statistics."""
    stats = get_usage_statistics(component, days)
    
    if component:
        panel(f"Usage Statistics: {component}", "Analytics")
        stats_data = stats.get("statistics", {})
        rows = [
            ["Total Operations", stats_data.get("total_operations", 0)],
            ["Successful", stats_data.get("successful", 0)],
            ["Failed", stats_data.get("failed", 0)],
            ["Avg Duration", f"{stats_data.get('avg_duration', 0.0):.2f}s"],
        ]
        table(["Metric", "Value"], rows)
    else:
        panel("Usage Statistics: All Components", "Analytics")
        all_stats = stats.get("all_components", {})
        log(f"Total Operations: {all_stats.get('total_operations', 0)}")
        log(f"Successful: {all_stats.get('successful', 0)}")
        log(f"Failed: {all_stats.get('failed', 0)}")


@app.command()
def trends(
    component: str = typer.Argument(..., help="Component name"),
    days: int = typer.Option(30, "--days", "-d", help="Number of days"),
):
    """Show performance trends."""
    trends_data = get_performance_trends(component, days)
    
    panel(f"Performance Trends: {component}", "Analytics")
    trend_info = trends_data.get("trends", {})
    rows = [
        ["Avg Duration", f"{trend_info.get('avg_duration', 0.0):.2f}s"],
        ["Total Operations", trend_info.get("total_operations", 0)],
        ["Success Rate", f"{trend_info.get('success_rate', 0.0) * 100:.1f}%"],
    ]
    table(["Metric", "Value"], rows)


@app.command()
def dependencies(
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Analyze dependency relationships."""
    analysis = get_dependency_analysis(manifests_dir)
    
    panel("Dependency Analysis", "Analytics")
    rows = [
        ["Total Components", analysis.get("total_components", 0)],
        ["Total Dependencies", analysis.get("total_dependencies", 0)],
        ["Avg Dependencies", f"{analysis.get('avg_dependencies', 0.0):.2f}"],
        ["Most Dependent", analysis.get("most_dependent", "N/A")],
    ]
    table(["Metric", "Value"], rows)


@app.command()
def health(
    days: int = typer.Option(30, "--days", "-d", help="Number of days"),
):
    """Show health trends."""
    trends = get_health_trends(days)
    log(f"Health trends for last {days} days")
    log(trends.get("trends", "Not available"))


