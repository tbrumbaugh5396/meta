"""Configuration management commands."""

import typer
from typing import Optional, List
from meta.utils.logger import log, success, error, table, panel
from meta.utils.config import get_config
from meta.utils.environment_manager import (
    add_environment,
    delete_environment,
    reset_environments,
    edit_environment,
    list_environments,
    show_environment,
)

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


@app.command()
def environment(
    action: str = typer.Argument(..., help="Action: add, delete, reset, edit, list, show"),
    env_name: Optional[str] = typer.Argument(None, help="Environment name"),
    from_env: Optional[str] = typer.Option(None, "--from", help="Copy from existing environment (for add)"),
    component: Optional[List[str]] = typer.Option(None, "--component", "-c", help="Component version pairs: 'component-name:version' (can be used multiple times)"),
    set_all: Optional[str] = typer.Option(None, "--set-all", help="Set all components to this version (for edit)"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Manage environments in manifests/environments.yaml."""
    
    if action == "list":
        envs = list_environments(manifests_dir)
        if not envs:
            log("No environments found")
            return
        
        panel("Environments", "Config")
        rows = []
        for env in envs:
            env_config = show_environment(env, manifests_dir)
            component_count = len(env_config) if env_config else 0
            rows.append([env, str(component_count)])
        table(["Environment", "Components"], rows)
        return
    
    if action == "show":
        if not env_name:
            error("Environment name required for 'show' action")
            raise typer.Exit(code=1)
        
        env_config = show_environment(env_name, manifests_dir)
        if not env_config:
            error(f"Environment '{env_name}' not found")
            raise typer.Exit(code=1)
        
        panel(f"Environment: {env_name}", "Config")
        rows = []
        for comp_name, version in sorted(env_config.items()):
            rows.append([comp_name, version])
        table(["Component", "Version"], rows)
        return
    
    if action == "add":
        if not env_name:
            error("Environment name required for 'add' action")
            raise typer.Exit(code=1)
        
        # Parse component versions if provided
        component_versions = None
        if component:
            component_versions = {}
            for comp_spec in component:
                if ':' not in comp_spec:
                    error(f"Invalid component specification: '{comp_spec}'. Use 'component-name:version'")
                    raise typer.Exit(code=1)
                comp_name, version = comp_spec.split(':', 1)
                component_versions[comp_name] = version
        
        if not add_environment(env_name, manifests_dir, from_env, component_versions):
            raise typer.Exit(code=1)
        return
    
    if action == "delete":
        if not env_name:
            error("Environment name required for 'delete' action")
            raise typer.Exit(code=1)
        
        if not delete_environment(env_name, manifests_dir):
            raise typer.Exit(code=1)
        return
    
    if action == "reset":
        if not typer.confirm("This will reset all environments to defaults (dev, staging, prod). Continue?"):
            log("Cancelled")
            return
        
        if not reset_environments(manifests_dir):
            raise typer.Exit(code=1)
        return
    
    if action == "edit":
        if not env_name:
            error("Environment name required for 'edit' action")
            raise typer.Exit(code=1)
        
        # Parse component versions if provided
        component_versions = None
        if component:
            component_versions = {}
            for comp_spec in component:
                if ':' not in comp_spec:
                    error(f"Invalid component specification: '{comp_spec}'. Use 'component-name:version'")
                    raise typer.Exit(code=1)
                comp_name, version = comp_spec.split(':', 1)
                component_versions[comp_name] = version
        
        if not edit_environment(env_name, manifests_dir, component_versions, set_all):
            raise typer.Exit(code=1)
        return
    
    error(f"Unknown action: {action}. Use: add, delete, reset, edit, list, or show")
    raise typer.Exit(code=1)

