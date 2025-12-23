"""Component info commands."""

import typer
from typing import Optional
from pathlib import Path
from meta.utils.logger import log, success, error, table, panel
from meta.utils.manifest import get_components
from meta.utils.git import get_current_version, get_commit_sha
from meta.utils.health import check_component_health
from meta.utils.dependencies import resolve_transitive_dependencies

app = typer.Typer(help="Show component information")


@app.command()
def component(
    component_name: str = typer.Argument(..., help="Component name"),
    env: Optional[str] = typer.Option(None, "--env", "-e", help="Environment"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Show detailed information about a component."""
    components = get_components(manifests_dir)
    
    if component_name not in components:
        error(f"Component {component_name} not found")
        raise typer.Exit(code=1)
    
    comp_data = components[component_name]
    
    # Get current state
    comp_path = Path(f"components/{component_name}")
    current_version = None
    current_commit = None
    exists = comp_path.exists()
    
    if exists:
        current_version = get_current_version(str(comp_path))
        current_commit = get_commit_sha(str(comp_path))
    
    # Get dependencies
    deps = resolve_transitive_dependencies(components)
    component_deps = deps.get(component_name, set())
    
    # Get health status
    health_status = check_component_health(component_name, env, manifests_dir, check_build=False, check_tests=False)
    
    # Display info
    panel(f"Component: {component_name}", "Info")
    
    rows = [
        ["Name", component_name],
        ["Type", comp_data.get("type", "unknown")],
        ["Repository", comp_data.get("repo", "N/A")],
        ["Manifest Version", comp_data.get("version", "N/A")],
        ["Build Target", comp_data.get("build_target", "N/A")],
        ["Exists Locally", "Yes" if exists else "No"],
    ]
    
    if current_version:
        rows.append(["Current Version", current_version])
    if current_commit:
        rows.append(["Current Commit", current_commit[:8] if current_commit else "N/A"])
    
    rows.append(["Health", "✅ Healthy" if health_status.healthy else "❌ Unhealthy"])
    rows.append(["Dependencies", f"{len(component_deps)} component(s)"])
    
    table(["Property", "Value"], rows)
    
    # Show dependencies
    if component_deps:
        log("\nDependencies:")
        for dep in sorted(component_deps):
            log(f"  - {dep}")
    
    # Show health details
    if not health_status.healthy:
        log("\nHealth Issues:")
        for err in health_status.errors:
            error(f"  - {err}")


