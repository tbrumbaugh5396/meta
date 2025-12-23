"""Component notification commands."""

import typer
from typing import Optional, List
from meta.utils.logger import log, success, error
from meta.utils.notifications import get_notification_manager

app = typer.Typer(help="Component notifications")


@app.command()
def setup(
    email: Optional[str] = typer.Option(None, "--email", help="Email address"),
    slack: Optional[str] = typer.Option(None, "--slack", help="Slack webhook URL"),
):
    """Setup notification channels."""
    manager = get_notification_manager()
    
    if manager.setup(email, slack):
        success("Notification channels configured")
    else:
        error("Failed to setup notifications")
        raise typer.Exit(code=1)


@app.command()
def subscribe(
    component: str = typer.Argument(..., help="Component name"),
    events: str = typer.Argument(..., help="Comma-separated events (update,failure,success)"),
):
    """Subscribe to component events."""
    manager = get_notification_manager()
    event_list = [e.strip() for e in events.split(",")]
    
    if manager.subscribe(component, event_list):
        success(f"Subscribed to {component} events: {', '.join(event_list)}")
    else:
        error("Failed to subscribe")
        raise typer.Exit(code=1)


@app.command()
def test():
    """Test notification setup."""
    manager = get_notification_manager()
    
    if manager.send_notification("test", "system", "Test notification from meta-repo CLI"):
        success("Test notification sent")
    else:
        error("Failed to send test notification")
        raise typer.Exit(code=1)


