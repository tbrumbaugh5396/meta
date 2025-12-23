"""Component history commands."""

import typer
from typing import Optional
from meta.utils.logger import log, table, panel
from meta.utils.history import get_component_history

app = typer.Typer(help="Component history")


@app.command()
def show(
    component: Optional[str] = typer.Argument(None, help="Component name (optional)"),
    limit: int = typer.Option(50, "--limit", "-n", help="Number of entries"),
    action: Optional[str] = typer.Option(None, "--action", "-a", help="Filter by action"),
):
    """Show component history."""
    history_manager = get_component_history()
    
    if component:
        history = history_manager.get_history(component, limit, action)
        
        if not history:
            log(f"No history found for: {component}")
            return
        
        panel(f"History for {component}: {len(history)} entry(ies)", "Component History")
        rows = []
        for entry in reversed(history):  # Show most recent first
            rows.append([
                entry.get("timestamp", "unknown"),
                entry.get("action", "unknown"),
                entry.get("version", "unknown"),
                str(entry.get("metadata", {}))
            ])
        
        table(["Timestamp", "Action", "Version", "Metadata"], rows)
    else:
        all_history = history_manager.get_all_history(limit)
        
        if not all_history:
            log("No history found")
            return
        
        panel(f"History for all components", "Component History")
        for comp_name, history in all_history.items():
            log(f"\n{comp_name}:")
            for entry in reversed(history[-10:]):  # Show last 10 per component
                log(f"  {entry.get('timestamp')} - {entry.get('action')} - {entry.get('version')}")


@app.command()
def clear(
    component: Optional[str] = typer.Argument(None, help="Component name (optional, clears all if omitted)"),
):
    """Clear component history."""
    history_manager = get_component_history()
    
    if history_manager.clear_history(component):
        if component:
            log(f"Cleared history for: {component}")
        else:
            log("Cleared all history")
    else:
        log("Failed to clear history")


