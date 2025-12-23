"""Vendor components for Linus-safe materialization."""

import typer
from pathlib import Path
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.manifest import get_components, find_meta_repo_root
from meta.utils.vendor import (
    vendor_component, is_vendored_mode, get_vendor_info,
    convert_to_vendored_mode, convert_to_reference_mode,
    convert_to_vendored_for_production
)

app = typer.Typer(help="Vendor components into meta-repo (Linus-safe mode)")


@app.command(name="import-component")
def import_component(
    component: str = typer.Argument(..., help="Component name to vendor"),
    force: bool = typer.Option(False, "--force", "-f", help="Re-import even if already vendored"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Import a component by copying its source into meta-repo."""
    if not is_vendored_mode(manifests_dir):
        error("Vendored mode not enabled. Set meta.mode: 'vendored' in components.yaml")
        raise typer.Exit(code=1)
    
    components = get_components(manifests_dir)
    if component not in components:
        error(f"Component '{component}' not found in manifest")
        raise typer.Exit(code=1)
    
    comp = components[component]
    
    if vendor_component(component, comp, manifests_dir, force):
        success(f"Successfully vendored {component}")
        log("Next steps:")
        log("  1. Review the vendored code")
        log("  2. Commit to meta-repo: git add components/ && git commit -m 'Vendor component'")
    else:
        error(f"Failed to vendor {component}")
        raise typer.Exit(code=1)


@app.command(name="import-all")
def import_all(
    force: bool = typer.Option(False, "--force", "-f", help="Re-import all components"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Import all components into meta-repo."""
    if not is_vendored_mode(manifests_dir):
        error("Vendored mode not enabled. Set meta.mode: 'vendored' in components.yaml")
        raise typer.Exit(code=1)
    
    components = get_components(manifests_dir)
    
    if not components:
        log("No components to vendor")
        return
    
    panel(f"Vendoring {len(components)} components", "Vendor All")
    
    results = []
    for name, comp in components.items():
        log(f"\nVendoring {name}...")
        success_result = vendor_component(name, comp, manifests_dir, force)
        results.append((name, success_result))
    
    # Summary
    successful = [name for name, ok in results if ok]
    failed = [name for name, ok in results if not ok]
    
    if successful:
        success(f"Successfully vendored {len(successful)} components")
    if failed:
        error(f"Failed to vendor {len(failed)} components: {', '.join(failed)}")
    
    if failed:
        raise typer.Exit(code=1)
    
    log("\nNext steps:")
    log("  1. Review the vendored code")
    log("  2. Commit to meta-repo: git add components/ && git commit -m 'Vendor all components'")


@app.command()
def status(
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Show vendor status of all components."""
    if not is_vendored_mode(manifests_dir):
        error("Vendored mode not enabled")
        raise typer.Exit(code=1)
    
    root = find_meta_repo_root()
    if not root:
        error("Could not find meta-repo root")
        raise typer.Exit(code=1)
    
    components = get_components(manifests_dir)
    
    if not components:
        log("No components defined")
        return
    
    rows = []
    for name, comp in components.items():
        comp_dir = root / "components" / name
        vendor_info = get_vendor_info(comp_dir) if comp_dir.exists() else None
        
        if vendor_info:
            status_icon = "✅"
            version = vendor_info.get("version", "unknown")
            vendored_at = vendor_info.get("vendored_at", "unknown")
            if len(vendored_at) > 10:
                vendored_at = vendored_at[:10]
        else:
            status_icon = "❌"
            version = comp.get("version", "unknown")
            vendored_at = "Not vendored"
        
        rows.append([status_icon, name, version, vendored_at])
    
    table(["Status", "Component", "Version", "Vendored At"], rows)


@app.command()
def convert(
    to_mode: str = typer.Argument(..., help="Target mode: 'vendored' or 'reference'"),
    force: bool = typer.Option(False, "--force", "-f", help="Force conversion even if already in target mode"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Convert between reference and vendored modes.
    
    Examples:
        meta vendor convert vendored    # Convert to vendored mode
        meta vendor convert reference  # Convert to reference mode
    """
    if to_mode not in ["vendored", "reference"]:
        error(f"Invalid mode: {to_mode}. Must be 'vendored' or 'reference'")
        raise typer.Exit(code=1)
    
    if to_mode == "vendored":
        if convert_to_vendored_mode(manifests_dir, force):
            success("Successfully converted to vendored mode")
        else:
            error("Failed to convert to vendored mode")
            raise typer.Exit(code=1)
    else:  # reference
        if convert_to_reference_mode(manifests_dir, force):
            success("Successfully converted to reference mode")
        else:
            error("Failed to convert to reference mode")
            raise typer.Exit(code=1)


@app.command(name="release")
def release(
    env: str = typer.Option("prod", "--env", "-e", help="Production environment name"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Release version tag (e.g., v1.0.0)"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-vendoring"),
):
    """Create a production release by converting to vendored mode.
    
    This command:
    1. Converts all components to vendored mode at production versions
    2. Generates production lock file with semantic versions
    3. Creates a self-contained, Linus-safe production release
    
    Workflow:
        # Development: Use reference mode
        meta apply --env dev  # Uses git repos
        
        # Production release: Convert to vendored
        meta vendor release --env prod --version v1.0.0
        git add manifests/ components/
        git commit -m "Production release v1.0.0"
        git tag -a v1.0.0 -m "Production release v1.0.0"
    
    Examples:
        meta vendor release                    # Convert to vendored for prod
        meta vendor release --env staging      # Convert for staging
        meta vendor release --version v2.0.0   # Tag with specific version
    """
    from meta.utils.git import git_available
    import subprocess
    
    if convert_to_vendored_for_production(env, manifests_dir, force):
        success(f"Production release ready for {env}")
        
        if version:
            if not git_available():
                log("Git not available - skipping tag creation")
            else:
                log(f"Creating release tag: {version}")
                try:
                    subprocess.run(
                        ["git", "tag", "-a", version, "-m", f"Production release {version}"],
                        check=True
                    )
                    success(f"Created release tag: {version}")
                except subprocess.CalledProcessError as e:
                    error(f"Failed to create tag: {e}")
        
        log("\n🎉 Production release is self-contained and Linus-safe!")
        log("The meta-repo now contains all source code with semantic versions.")
    else:
        error("Failed to create production release")
        raise typer.Exit(code=1)

