"""Component discovery commands."""

import typer
import yaml
from pathlib import Path
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.discovery import discover_components, validate_component_structure, generate_manifest_entry

app = typer.Typer(help="Discover components")


@app.command()
def components(
    path: str = typer.Argument(".", help="Path to search for components"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", "-r", help="Recursive search"),
    add_to_manifest: bool = typer.Option(False, "--add-to-manifest", help="Add discovered components to manifest"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Discover components in a directory."""
    log(f"Discovering components in: {path}")
    
    discovered = discover_components(path, recursive)
    
    if not discovered:
        log("No components discovered")
        return
    
    panel(f"Discovered {len(discovered)} component(s)", "Discovery")
    rows = []
    for comp in discovered:
        valid, errors = validate_component_structure(Path(comp["path"]))
        status = "✅" if valid else "⚠️"
        rows.append([
            status,
            comp["name"],
            comp["type"],
            comp["path"],
            f"{len(errors)} issue(s)" if errors else "Valid"
        ])
    
    table(["Status", "Name", "Type", "Path", "Validation"], rows)
    
    if add_to_manifest:
        manifest_path = Path(manifests_dir) / "components.yaml"
        if not manifest_path.exists():
            error(f"Manifest file not found: {manifest_path}")
            return
        
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f) or {}
        
        components_dict = manifest.get("components", {})
        added = 0
        
        for comp in discovered:
            if comp["name"] in components_dict:
                log(f"Skipping {comp['name']} (already in manifest)")
                continue
            
            entry = generate_manifest_entry(comp)
            components_dict[comp["name"]] = entry
            added += 1
        
        manifest["components"] = components_dict
        
        with open(manifest_path, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
        
        success(f"Added {added} component(s) to manifest")


