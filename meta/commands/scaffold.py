"""Component scaffolding commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error
from meta.utils.scaffold import create_component_structure, generate_manifest_entry
import yaml

app = typer.Typer(help="Scaffold new components")


@app.command()
def component(
    component_name: str = typer.Argument(..., help="Component name"),
    component_type: str = typer.Option("bazel", "--type", "-t", help="Component type (bazel, python, npm)"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Component description"),
    component_dir: str = typer.Option("components", "--dir", help="Component directory"),
    add_to_manifest: bool = typer.Option(False, "--add-to-manifest", help="Add to manifests/components.yaml"),
    repo_url: Optional[str] = typer.Option(None, "--repo", "-r", help="Repository URL"),
    version: str = typer.Option("0.1.0", "--version", "-v", help="Initial version"),
):
    """Scaffold a new component."""
    log(f"Scaffolding component: {component_name} (type: {component_type})")
    
    if create_component_structure(component_name, component_type, description, component_dir):
        if add_to_manifest:
            # Add to manifest
            manifest_path = Path("manifests/components.yaml")
            if manifest_path.exists():
                with open(manifest_path) as f:
                    manifest = yaml.safe_load(f) or {}
                
                components = manifest.get("components", {})
                if component_name in components:
                    error(f"Component {component_name} already in manifest")
                    return
                
                entry = generate_manifest_entry(component_name, component_type, repo_url, version)
                components[component_name] = entry
                manifest["components"] = components
                
                with open(manifest_path, 'w') as f:
                    yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
                
                success(f"Added {component_name} to manifest")
            else:
                log("Manifest file not found, skipping manifest update")
        
        success(f"Component {component_name} scaffolded successfully!")
    else:
        error("Failed to scaffold component")
        raise typer.Exit(code=1)


