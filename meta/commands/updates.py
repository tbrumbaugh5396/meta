"""Component update commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.updates import check_component_updates, check_all_updates
from meta.utils.manifest import get_components
from meta.commands.apply import apply_component

app = typer.Typer(help="Check and update components")


@app.command()
def check(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Check specific component"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Check for component updates."""
    if component:
        update_info = check_component_updates(component, manifests_dir)
        if not update_info:
            log(f"No update information available for {component}")
            return
        
        panel(f"Update Status: {component}", "Updates")
        rows = [
            ["Current Version", update_info["current_version"]],
            ["Latest Version", update_info["latest_version"]],
            ["Update Available", "Yes" if update_info["update_available"] else "No"],
        ]
        table(["Property", "Value"], rows)
        
        if update_info["update_available"]:
            log(f"\nUpdate available: {update_info['current_version']} -> {update_info['latest_version']}")
    else:
        log("Checking all components for updates...")
        updates = check_all_updates(manifests_dir)
        
        if not updates:
            success("All components are up to date!")
            return
        
        panel(f"Updates Available: {len(updates)} component(s)", "Updates")
        rows = []
        for update in updates:
            rows.append([
                update["component"],
                update["current_version"],
                update["latest_version"],
                "Yes" if update["update_available"] else "No"
            ])
        
        table(["Component", "Current", "Latest", "Update Available"], rows)


@app.command()
def update(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Update specific component"),
    all: bool = typer.Option(False, "--all", "-a", help="Update all components"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    env: str = typer.Option("dev", "--env", "-e", help="Environment"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be updated"),
):
    """Update components to latest versions."""
    if not component and not all:
        error("Specify --component or --all")
        raise typer.Exit(code=1)
    
    if component:
        update_info = check_component_updates(component, manifests_dir)
        if not update_info or not update_info["update_available"]:
            log(f"No updates available for {component}")
            return
        
        if dry_run:
            log(f"Would update {component} from {update_info['current_version']} to {update_info['latest_version']}")
            return
        
        # Update manifest
        import yaml
        manifest_path = Path(manifests_dir) / "components.yaml"
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f) or {}
        
        components = manifest.get("components", {})
        if component in components:
            components[component]["version"] = update_info["latest_version"]
            manifest["components"] = components
            
            with open(manifest_path, 'w') as f:
                yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
            
            success(f"Updated {component} to {update_info['latest_version']} in manifest")
            
            # Apply the update
            log(f"Applying update for {component}...")
            comp_data = components[component]
            if apply_component(component, comp_data, env, manifests_dir):
                success(f"Successfully updated {component}")
            else:
                error(f"Failed to apply update for {component}")
    elif all:
        updates = check_all_updates(manifests_dir)
        if not updates:
            success("All components are up to date!")
            return
        
        if dry_run:
            log(f"Would update {len(updates)} component(s):")
            for update in updates:
                log(f"  - {update['component']}: {update['current_version']} -> {update['latest_version']}")
            return
        
        # Update all
        for update in updates:
            # Recursively call update for each component
            # This is a simplified approach
            log(f"Updating {update['component']}...")
            # In a real implementation, we'd call the update logic here


