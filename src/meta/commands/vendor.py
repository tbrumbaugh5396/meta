"""Vendor components for Linus-safe materialization."""

import typer
from pathlib import Path
from typing import Optional
from meta.utils.logger import log, success, error, warning, table, panel
from meta.utils.manifest import get_components, find_meta_repo_root
from meta.utils.vendor import (
    vendor_component, is_vendored_mode, get_vendor_info,
    convert_to_vendored_mode, convert_to_reference_mode,
    convert_to_vendored_for_production,
    convert_to_vendored_mode_enhanced, verify_conversion
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
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without making them"),
    continue_on_error: bool = typer.Option(False, "--continue-on-error", help="Continue converting other components if one fails"),
    check_secrets: bool = typer.Option(True, "--check-secrets/--no-check-secrets", help="Check for secrets during vendor"),
    fail_on_secrets: bool = typer.Option(False, "--fail-on-secrets", help="Fail if secrets are detected"),
    create_backup: bool = typer.Option(True, "--backup/--no-backup", help="Create backup before conversion"),
    atomic: bool = typer.Option(True, "--atomic/--no-atomic", help="Use atomic transaction (all-or-nothing)"),
    respect_gitignore: bool = typer.Option(True, "--respect-gitignore/--no-respect-gitignore", help="Respect .gitignore patterns"),
    verify: bool = typer.Option(True, "--verify/--no-verify", help="Verify conversion after completion"),
    resume: bool = typer.Option(False, "--resume", help="Resume from checkpoint"),
    checkpoint_id: Optional[str] = typer.Option(None, "--checkpoint", "-c", help="Specific checkpoint ID to resume from"),
    changeset: Optional[str] = typer.Option(None, "--changeset", help="Changeset ID to associate with conversion"),
):
    """Convert between reference and vendored modes with enhanced safety features.
    
    Examples:
        meta vendor convert vendored                    # Convert to vendored mode
        meta vendor convert vendored --dry-run          # Preview conversion
        meta vendor convert vendored --continue-on-error  # Continue on errors
        meta vendor convert reference                   # Convert to reference mode
    """
    if to_mode not in ["vendored", "reference"]:
        error(f"Invalid mode: {to_mode}. Must be 'vendored' or 'reference'")
        raise typer.Exit(code=1)
    
    if to_mode == "vendored":
        # Use enhanced conversion for vendored mode
        success_flag, results = convert_to_vendored_mode_enhanced(
            manifests_dir=manifests_dir,
            force=force,
            dry_run=dry_run,
            continue_on_error=continue_on_error,
            check_secrets=check_secrets,
            fail_on_secrets=fail_on_secrets,
            create_backup=create_backup,
            atomic=atomic,
            respect_gitignore=respect_gitignore,
            resume=resume,
            checkpoint_id=checkpoint_id,
            changeset_id=changeset
        )
        
        if success_flag:
            if not dry_run:
                success("Successfully converted to vendored mode")
                
                # Verify conversion
                if verify:
                    log("Verifying conversion...")
                    is_valid, verification_details = verify_conversion(manifests_dir)
                    if is_valid:
                        success(f"Verification passed: {verification_details['components_valid']}/{verification_details['components_checked']} components valid")
                    else:
                        warning(f"Verification found issues: {verification_details['components_invalid']} components invalid")
                        for err in verification_details['errors'][:5]:
                            warning(f"  - {err}")
            else:
                success("Dry-run completed (no changes made)")
        else:
            error("Failed to convert to vendored mode")
            if results.get('errors'):
                for err in results['errors'][:10]:
                    error(f"  - {err}")
            raise typer.Exit(code=1)
    else:  # reference
        # Use standard conversion for reference mode (can be enhanced later)
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


@app.command(name="verify")
def verify(
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    check_integrity: bool = typer.Option(True, "--check-integrity/--no-check-integrity", help="Check file integrity"),
):
    """Verify that a vendor conversion was successful."""
    is_valid, details = verify_conversion(manifests_dir, check_integrity=check_integrity)
    
    if is_valid:
        success("Conversion verification passed")
        log(f"  ✓ {details['components_valid']}/{details['components_checked']} components valid")
    else:
        error("Conversion verification failed")
        log(f"  ✗ {details['components_invalid']}/{details['components_checked']} components invalid")
        for err in details['errors'][:10]:
            error(f"    - {err}")
        raise typer.Exit(code=1)


@app.command(name="backup")
def backup(
    backup_name: Optional[str] = typer.Option(None, "--name", "-n", help="Backup name (defaults to timestamp)"),
    include_components: bool = typer.Option(True, "--include-components/--no-include-components", help="Include components directory"),
):
    """Create a backup of the current meta-repo state."""
    from meta.utils.vendor_backup import create_backup
    
    backup_path = create_backup(backup_name, include_components=include_components)
    if backup_path:
        success(f"Backup created: {backup_path}")
    else:
        error("Failed to create backup")
        raise typer.Exit(code=1)


@app.command(name="restore")
def restore(
    backup_name: str = typer.Argument(..., help="Backup name to restore"),
    restore_components: bool = typer.Option(True, "--restore-components/--no-restore-components", help="Restore components directory"),
):
    """Restore from a backup."""
    from meta.utils.vendor_backup import restore_backup
    
    if restore_backup(backup_name, restore_components=restore_components):
        success(f"Restored from backup: {backup_name}")
    else:
        error("Failed to restore from backup")
        raise typer.Exit(code=1)


@app.command(name="list-backups")
def list_backups():
    """List all available backups."""
    from meta.utils.vendor_backup import list_backups
    
    backups = list_backups()
    if not backups:
        log("No backups found")
        return
    
    rows = []
    for backup in backups:
        backup_name = backup.get('backup_name', 'unknown')
        created_at = backup.get('created_at', 'unknown')
        if len(created_at) > 19:
            created_at = created_at[:19]
        includes_components = backup.get('includes_components', False)
        rows.append([backup_name, created_at, "✓" if includes_components else "✗"])
    
    table(["Backup Name", "Created At", "Components"], rows)


@app.command(name="resume")
def resume(
    checkpoint_id: Optional[str] = typer.Option(None, "--checkpoint", "-c", help="Checkpoint ID (defaults to latest)"),
    retry_failed: bool = typer.Option(True, "--retry-failed/--no-retry-failed", help="Retry previously failed components"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Resume a conversion from a checkpoint."""
    from meta.utils.vendor_resume import resume_conversion
    
    checkpoint = resume_conversion(
        checkpoint_id=checkpoint_id,
        skip_completed=True,
        retry_failed=retry_failed
    )
    
    if not checkpoint:
        error("No checkpoint found to resume")
        raise typer.Exit(code=1)
    
    # Continue with conversion using the checkpoint
    success_flag, results = convert_to_vendored_mode_enhanced(
        manifests_dir=manifests_dir,
        resume=True,
        checkpoint_id=checkpoint.checkpoint_id,
        continue_on_error=True,
        atomic=False  # Can't be atomic when resuming
    )
    
    if success_flag:
        success("Conversion resumed and completed")
    else:
        error("Conversion resumed but some components failed")
        raise typer.Exit(code=1)


@app.command(name="list-checkpoints")
def list_checkpoints():
    """List all available conversion checkpoints."""
    from meta.utils.vendor_resume import list_checkpoints
    
    checkpoints = list_checkpoints()
    if not checkpoints:
        log("No checkpoints found")
        return
    
    rows = []
    for checkpoint in checkpoints:
        checkpoint_id = checkpoint.get('checkpoint_id', 'unknown')
        created_at = checkpoint.get('created_at', 'unknown')
        if len(created_at) > 19:
            created_at = created_at[:19]
        target_mode = checkpoint.get('target_mode', 'unknown')
        completed = len(checkpoint.get('completed_components', []))
        total = completed + len(checkpoint.get('pending_components', []))
        progress = f"{completed}/{total}" if total > 0 else "0/0"
        rows.append([checkpoint_id, created_at, target_mode, progress])
    
    table(["Checkpoint ID", "Created At", "Target Mode", "Progress"], rows)

