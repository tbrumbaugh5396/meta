"""OS-level declarative management commands."""

import typer
from pathlib import Path
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.os_config import get_os_manifest
from meta.utils.os_provisioning import get_provisioning_engine
from meta.utils.os_state import get_os_state_manager
from meta.utils.os_build import get_os_build_system
from meta.utils.os_deploy import get_os_deployment
from meta.utils.os_monitoring import get_os_monitoring

app = typer.Typer(help="OS-level declarative management")


@app.command()
def init(
    manifest_path: str = typer.Option("os-manifest.yaml", "--manifest", "-m", help="Manifest file path"),
):
    """Initialize OS manifest."""
    manifest = get_os_manifest(Path(manifest_path))
    manifest.save()
    success(f"OS manifest initialized: {manifest_path}")


@app.command()
def add(
    item_type: str = typer.Argument(..., help="Item type (package/service/user/file)"),
    name: str = typer.Argument(..., help="Item name/path"),
    manifest_path: str = typer.Option("os-manifest.yaml", "--manifest", "-m", help="Manifest file path"),
    **kwargs
):
    """Add item to OS manifest."""
    manifest = get_os_manifest(Path(manifest_path))
    
    if item_type == "package":
        version = kwargs.get("version")
        source = kwargs.get("source")
        manifest.add_package(name, version, source)
    elif item_type == "service":
        enabled = kwargs.get("enabled", True)
        manifest.add_service(name, enabled)
    elif item_type == "user":
        groups = kwargs.get("groups", "").split(",") if kwargs.get("groups") else None
        home = kwargs.get("home")
        manifest.add_user(name, groups, home)
    elif item_type == "file":
        content = kwargs.get("content")
        source = kwargs.get("source")
        mode = kwargs.get("mode")
        owner = kwargs.get("owner")
        manifest.add_file(name, content, source, mode, owner)
    else:
        error(f"Unknown item type: {item_type}")
        raise typer.Exit(code=1)
    
    manifest.save()
    success(f"Added {item_type}: {name}")


@app.command()
def validate(
    manifest_path: str = typer.Option("os-manifest.yaml", "--manifest", "-m", help="Manifest file path"),
):
    """Validate OS manifest."""
    manifest = get_os_manifest(Path(manifest_path))
    errors = manifest.validate()
    
    if errors:
        error("Validation failed:")
        for err in errors:
            error(f"  • {err}")
        raise typer.Exit(code=1)
    else:
        success("OS manifest is valid")


@app.command()
def provision(
    manifest_path: str = typer.Option("os-manifest.yaml", "--manifest", "-m", help="Manifest file path"),
    provider: str = typer.Option("ansible", "--provider", "-p", help="Provisioning provider"),
    target: Optional[str] = typer.Option(None, "--target", "-t", help="Target host"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Dry run mode"),
):
    """Provision OS from manifest."""
    engine = get_provisioning_engine()
    
    if engine.provision(Path(manifest_path), provider, target, dry_run):
        success("OS provisioning completed")
    else:
        error("Provisioning failed")
        raise typer.Exit(code=1)


@app.command()
def state(
    action: str = typer.Argument(..., help="Action (capture/compare/restore)"),
    manifest_path: str = typer.Option("os-manifest.yaml", "--manifest", "-m", help="Manifest file path"),
):
    """Manage OS state."""
    state_manager = get_os_state_manager()
    
    if action == "capture":
        if state_manager.capture_state(Path(manifest_path)):
            success("OS state captured")
        else:
            error("Failed to capture state")
            raise typer.Exit(code=1)
    elif action == "compare":
        diff = state_manager.compare_state(Path(manifest_path))
        
        if "error" in diff:
            error(diff["error"])
            raise typer.Exit(code=1)
        
        panel("OS State Comparison", "State Diff")
        
        # Show differences
        if diff.get("packages", {}).get("missing"):
            log(f"Missing packages: {', '.join(diff['packages']['missing'])}")
        if diff.get("services", {}).get("missing"):
            log(f"Missing services: {', '.join(diff['services']['missing'])}")
        if diff.get("users", {}).get("missing"):
            log(f"Missing users: {', '.join(diff['users']['missing'])}")
        
        if not any(diff.values()):
            success("OS state matches manifest")
    elif action == "restore":
        if state_manager.restore_state():
            success("OS state restored")
        else:
            error("Failed to restore state")
            raise typer.Exit(code=1)
    else:
        error(f"Unknown action: {action}")
        raise typer.Exit(code=1)


@app.command()
def build(
    manifest_path: str = typer.Option("os-manifest.yaml", "--manifest", "-m", help="Manifest file path"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output image name"),
    format: str = typer.Option("docker", "--format", "-f", help="Image format (docker/iso/qcow2)"),
):
    """Build OS image from manifest."""
    build_system = get_os_build_system()
    
    if build_system.build_image(Path(manifest_path), output, format):
        success("OS image built")
    else:
        error("Build failed")
        raise typer.Exit(code=1)


@app.command()
def deploy(
    manifest_path: str = typer.Option("os-manifest.yaml", "--manifest", "-m", help="Manifest file path"),
    target: str = typer.Option("local", "--target", "-t", help="Deployment target"),
    method: str = typer.Option("provision", "--method", "-m", help="Deployment method"),
):
    """Deploy OS configuration."""
    deployment = get_os_deployment()
    
    if deployment.deploy(Path(manifest_path), target, method):
        success("OS deployment completed")
    else:
        error("Deployment failed")
        raise typer.Exit(code=1)


@app.command()
def monitor(
    action: str = typer.Argument(..., help="Action (metrics/compliance)"),
    manifest_path: str = typer.Option("os-manifest.yaml", "--manifest", "-m", help="Manifest file path"),
):
    """Monitor OS."""
    monitoring = get_os_monitoring()
    
    if action == "metrics":
        metrics = monitoring.collect_metrics()
        panel("OS Metrics", "Monitoring")
        log(f"System: {metrics.get('system', {})}")
        log(f"Packages: {metrics.get('packages', {})}")
        log(f"Services: {metrics.get('services', {})}")
        log(f"Resources: {metrics.get('resources', {})}")
    elif action == "compliance":
        compliance = monitoring.check_compliance(Path(manifest_path))
        
        if compliance.get("compliant"):
            success("OS is compliant with manifest")
        else:
            error("OS compliance issues:")
            for issue in compliance.get("issues", []):
                error(f"  • {issue}")
            raise typer.Exit(code=1)
    else:
        error(f"Unknown action: {action}")
        raise typer.Exit(code=1)


