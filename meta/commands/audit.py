"""Audit logging commands."""

import typer
from typing import Optional
from datetime import datetime
from meta.utils.logger import log, success, error, table, panel
from meta.utils.audit import get_audit_logger

app = typer.Typer(help="Audit logging")


@app.command()
def log(
    action: Optional[str] = typer.Option(None, "--action", help="Filter by action"),
    user: Optional[str] = typer.Option(None, "--user", help="Filter by user"),
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Filter by component"),
    since: Optional[str] = typer.Option(None, "--since", help="Since date (ISO format)"),
    days: Optional[int] = typer.Option(None, "--days", "-d", help="Last N days"),
    limit: int = typer.Option(100, "--limit", "-l", help="Limit results"),
):
    """Show audit log."""
    logger = get_audit_logger()
    
    since_date = None
    if since:
        try:
            since_date = datetime.fromisoformat(since.replace("Z", "+00:00"))
        except:
            error(f"Invalid date format: {since}")
            raise typer.Exit(code=1)
    
    entries = logger.query(action=action, user=user, component=component,
                          since=since_date, days=days)
    
    if not entries:
        log("No audit log entries found")
        return
    
    # Limit results
    entries = entries[-limit:]
    
    panel(f"Audit Log ({len(entries)} entries)", "Audit")
    rows = []
    for entry in entries:
        rows.append([
            entry.get("timestamp", "")[:19],  # Truncate to date/time
            entry.get("user", "unknown"),
            entry.get("action", "unknown"),
            entry.get("component", "N/A"),
            "✅" if entry.get("success") else "❌"
        ])
    
    table(["Timestamp", "User", "Action", "Component", "Status"], rows)


