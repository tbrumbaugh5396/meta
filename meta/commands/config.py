"""Configuration management commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.config import get_config

app = typer.Typer(help="Manage configuration")


@app.command()
def get(
    key: Optional[str] = typer.Argument(None, help="Config key (e.g., 'default_env' or 'remote_cache')"),
    global_config: bool = typer.Option(False, "--global", "-g", help="Use global config"),
):
    """Get config value(s)."""
    config = get_config()
    
    if key:
        value = config.get(key)
        if value is None:
            error(f"Config key '{key}' not found")
            raise typer.Exit(code=1)
        log(f"{key} = {value}")
    else:
        # Show all config
        all_config = config.get_all()
        if not all_config:
            log("No configuration found")
            return
        
        panel("Configuration", "Config")
        rows = []
        for k, v in sorted(all_config.items()):
            rows.append([k, str(v)])
        table(["Key", "Value"], rows)


@app.command()
def set(
    key: str = typer.Argument(..., help="Config key"),
    value: str = typer.Argument(..., help="Config value"),
    global_config: bool = typer.Option(False, "--global", "-g", help="Set in global config"),
):
    """Set config value."""
    config = get_config()
    
    # Try to parse value as appropriate type
    parsed_value = value
    if value.lower() == "true":
        parsed_value = True
    elif value.lower() == "false":
        parsed_value = False
    elif value.isdigit():
        parsed_value = int(value)
    elif value.replace('.', '', 1).isdigit():
        parsed_value = float(value)
    
    if config.set(key, parsed_value, global_config=global_config):
        config_type = "global" if global_config else "project"
        success(f"Set {key} = {parsed_value} in {config_type} config")
    else:
        error("Failed to set config value")
        raise typer.Exit(code=1)


@app.command()
def init(
    global_config: bool = typer.Option(False, "--global", "-g", help="Initialize global config"),
):
    """Initialize config file with defaults."""
    config = get_config()
    
    if config.init_config(global_config=global_config):
        config_type = "global" if global_config else "project"
        success(f"Initialized {config_type} config file")
    else:
        error("Failed to initialize config")
        raise typer.Exit(code=1)


@app.command()
def unset(
    key: str = typer.Argument(..., help="Config key to remove"),
    global_config: bool = typer.Option(False, "--global", "-g", help="Remove from global config"),
):
    """Remove config value."""
    config = get_config()
    
    # Set to None to remove
    if config.set(key, None, global_config=global_config):
        config_type = "global" if global_config else "project"
        success(f"Removed {key} from {config_type} config")
    else:
        error("Failed to remove config value")
        raise typer.Exit(code=1)


