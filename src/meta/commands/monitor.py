"""Component monitoring commands."""

import typer
from typing import Optional, List
from meta.utils.logger import log, success, error, table
from meta.utils.monitoring_integration import get_monitoring_integration

app = typer.Typer(help="Component monitoring")


@app.command()
def setup(
    provider: str = typer.Argument(..., help="Monitoring provider (prometheus/datadog/newrelic)"),
    endpoint: Optional[str] = typer.Option(None, "--endpoint", help="Provider endpoint"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API key"),
):
    """Setup monitoring provider."""
    integration = get_monitoring_integration()
    
    if integration.setup(provider, endpoint, api_key):
        success(f"Monitoring provider {provider} configured")
    else:
        error("Failed to setup monitoring")
        raise typer.Exit(code=1)


@app.command()
def register(
    component: str = typer.Argument(..., help="Component name"),
    metrics: str = typer.Option("", "--metrics", help="Comma-separated metrics"),
):
    """Register component with monitoring."""
    integration = get_monitoring_integration()
    metrics_list = [m.strip() for m in metrics.split(",")] if metrics else []
    
    if integration.register_component(component, metrics_list):
        success(f"Registered {component} with monitoring")
    else:
        error("Failed to register component")
        raise typer.Exit(code=1)


@app.command()
def metrics(
    component: str = typer.Argument(..., help="Component name"),
    time_range: str = typer.Option("1h", "--range", help="Time range"),
):
    """Get component metrics."""
    integration = get_monitoring_integration()
    metrics_data = integration.get_metrics(component, time_range)
    
    log(f"Metrics for {component} ({time_range}):")
    log(f"  {metrics_data}")


@app.command()
def alerts(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Component name"),
):
    """Get alerts."""
    integration = get_monitoring_integration()
    alerts_list = integration.get_alerts(component)
    
    if not alerts_list:
        log("No active alerts")
        return
    
    rows = []
    for alert in alerts_list:
        rows.append([
            alert.get("component", "unknown"),
            alert.get("severity", "unknown"),
            alert.get("message", "unknown")
        ])
    
    table(["Component", "Severity", "Message"], rows)


