"""Plugin management commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table
from meta.utils.plugins import get_plugin_manager

app = typer.Typer(help="Plugin management")


@app.command()
def install(
    plugin_name: str = typer.Argument(..., help="Plugin name or path"),
    plugin_path: Optional[str] = typer.Option(None, "--path", help="Plugin file path"),
):
    """Install a plugin."""
    manager = get_plugin_manager()
    
    if manager.load_plugin(plugin_name, plugin_path):
        success(f"Plugin {plugin_name} installed")
    else:
        error("Failed to install plugin")
        raise typer.Exit(code=1)


@app.command()
def list():
    """List installed plugins."""
    manager = get_plugin_manager()
    plugins = manager.list_plugins()
    
    if not plugins:
        log("No plugins installed")
        return
    
    rows = []
    for plugin_name in plugins:
        plugin = manager.get_plugin(plugin_name)
        rows.append([plugin_name, "Loaded" if plugin else "Error"])
    
    table(["Plugin", "Status"], rows)


@app.command()
def uninstall(
    plugin_name: str = typer.Argument(..., help="Plugin name"),
):
    """Uninstall a plugin."""
    manager = get_plugin_manager()
    
    if plugin_name in manager.plugins:
        del manager.plugins[plugin_name]
        success(f"Plugin {plugin_name} uninstalled")
    else:
        error(f"Plugin {plugin_name} not found")
        raise typer.Exit(code=1)


