"""Plan changes for meta-repo."""

import typer
from typing import Optional, Dict, Any
from meta.utils.logger import log, success, table, panel
from meta.utils.manifest import get_components, get_environment_config
from meta.utils.version import compare_versions
from meta.utils.git import get_current_version

app = typer.Typer(help="Plan changes for meta-repo")


def compute_changes(env: str, manifests_dir: str = "manifests") -> Dict[str, Any]:
    """Compute planned changes."""
    components = get_components(manifests_dir)
    env_config = get_environment_config(env, manifests_dir)
    
    changes = {
        "upgrades": [],
        "downgrades": [],
        "new": [],
        "unchanged": []
    }
    
    for name, comp in components.items():
        desired_version = comp.get("version", "unknown")
        comp_env = env_config.get(name, env)
        
        # Try to get current version (if component is checked out)
        current_version = get_current_version(f"components/{name}")
        
        if current_version is None:
            changes["new"].append({
                "component": name,
                "version": desired_version,
                "type": comp.get("type", "unknown")
            })
        else:
            comparison = compare_versions(current_version, desired_version)
            if comparison < 0:
                changes["upgrades"].append({
                    "component": name,
                    "current": current_version,
                    "desired": desired_version
                })
            elif comparison > 0:
                changes["downgrades"].append({
                    "component": name,
                    "current": current_version,
                    "desired": desired_version
                })
            else:
                changes["unchanged"].append({
                    "component": name,
                    "version": desired_version
                })
    
    return changes


@app.callback(invoke_without_command=True)
def plan(
    ctx: typer.Context,
    env: str = typer.Option("dev", "--env", "-e", help="Environment to plan for"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Plan for specific component only"),
):
    """Show planned changes before applying."""
    # Only run if no subcommands were invoked
    if ctx.invoked_subcommand is None:
        log(f"Planning changes for environment: {env}")
        
        changes = compute_changes(env, manifests_dir)
        
        if component:
            # Filter to specific component
            all_changes = changes["upgrades"] + changes["downgrades"] + changes["new"] + changes["unchanged"]
            filtered = [c for c in all_changes if c.get("component") == component]
            if not filtered:
                log(f"No changes planned for component: {component}")
                return
            changes = {
                "upgrades": [c for c in changes["upgrades"] if c["component"] == component],
                "downgrades": [c for c in changes["downgrades"] if c["component"] == component],
                "new": [c for c in changes["new"] if c["component"] == component],
                "unchanged": [c for c in changes["unchanged"] if c["component"] == component]
            }
        
        # Display changes
        if changes["upgrades"]:
            panel("Version Upgrades", "Upgrades")
            rows = [[c["component"], c["current"], "→", c["desired"]] for c in changes["upgrades"]]
            table(["Component", "Current", "", "Desired"], rows)
        
        if changes["downgrades"]:
            panel("Version Downgrades", "Downgrades")
            rows = [[c["component"], c["current"], "→", c["desired"]] for c in changes["downgrades"]]
            table(["Component", "Current", "", "Desired"], rows)
        
        if changes["new"]:
            panel("New Components", "New")
            rows = [[c["component"], c["version"], c["type"]] for c in changes["new"]]
            table(["Component", "Version", "Type"], rows)
        
        if changes["unchanged"]:
            log(f"{len(changes['unchanged'])} components unchanged")
        
        total_changes = len(changes["upgrades"]) + len(changes["downgrades"]) + len(changes["new"])
        if total_changes > 0:
            success(f"Planned {total_changes} change(s)")
        else:
            log("No changes planned")

