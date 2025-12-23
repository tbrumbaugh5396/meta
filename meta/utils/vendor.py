"""Vendoring utilities for Linus-safe materialization."""

import shutil
import subprocess
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from meta.utils.logger import log, error, success, warning
from meta.utils.git import git_available, clone_repo, checkout_version
from meta.utils.manifest import get_components, find_meta_repo_root, load_yaml, get_environment_config
from meta.utils.dependencies import get_dependency_order
from meta.utils.vendor_network import git_clone_with_retry, git_checkout_with_retry
from meta.utils.secret_detection import detect_secrets_in_component, should_exclude_file
from meta.utils.semver import parse_version
from meta.utils.vendor_resume import (
    create_checkpoint, load_checkpoint, resume_conversion,
    get_latest_checkpoint, cleanup_checkpoint
)


def is_vendored_mode(manifests_dir: str = "manifests") -> bool:
    """Check if meta-repo is in vendored mode."""
    try:
        manifest = load_yaml(f"{manifests_dir}/components.yaml")
        meta = manifest.get("meta", {})
        return meta.get("mode", "reference") == "vendored"
    except:
        return False


def vendor_component(
    name: str,
    comp: Dict[str, Any],
    manifests_dir: str = "manifests",
    force: bool = False,
    check_secrets: bool = True,
    fail_on_secrets: bool = False,
    respect_gitignore: bool = True
) -> bool:
    """Vendor a component by copying its source into meta-repo.
    
    This creates a Linus-safe materialized state where the meta-repo
    contains actual source code, not references.
    
    Args:
        name: Component name
        comp: Component configuration from manifest
        manifests_dir: Manifests directory
        force: Force re-import even if already vendored
        check_secrets: Whether to check for secrets
        fail_on_secrets: Whether to fail if secrets are detected
        respect_gitignore: Whether to respect .gitignore patterns
    
    Returns:
        True if successful, False otherwise
    """
    if not git_available():
        error("Git is not available")
        return False
    
    repo_url = comp.get("repo", "")
    version = comp.get("version", "latest")
    
    if not repo_url:
        error(f"No repository URL specified for {name}")
        return False
    
    root = find_meta_repo_root()
    if not root:
        error("Could not find meta-repo root")
        return False
    
    comp_dir = root / "components" / name
    
    # Check if already vendored
    if comp_dir.exists() and not force:
        vendor_info = get_vendor_info(comp_dir)
        if vendor_info:
            log(f"Component {name} already vendored at version {vendor_info.get('version', 'unknown')}")
            log("Use --force to re-import")
            return True
    
    log(f"Vendoring {name}@{version} from {repo_url}")
    
    # Clone to temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / name
        
        # Clone repository with retry logic
        if not git_clone_with_retry(repo_url, str(tmp_path), max_retries=3):
            error(f"Failed to clone {repo_url} after retries")
            return False
        
        # Checkout specific version with retry logic
        if version and version != "latest":
            if not git_checkout_with_retry(str(tmp_path), version, max_retries=3):
                error(f"Failed to checkout version {version} after retries")
                return False
            log(f"Checked out version {version}")
        
        # Check for secrets before copying
        if check_secrets:
            is_safe, secret_results = detect_secrets_in_component(tmp_path, fail_on_secrets=fail_on_secrets)
            if not is_safe:
                if fail_on_secrets:
                    error(f"Secrets detected in {name}, aborting vendor")
                    return False
                else:
                    warning(f"Potential secrets detected in {name} (continuing anyway)")
        
        # Remove .git directory (we don't want git history)
        git_dir = tmp_path / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir)
        
        # Copy source to components directory
        if comp_dir.exists():
            shutil.rmtree(comp_dir)
        
        comp_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy with optional .gitignore filtering
        if respect_gitignore:
            # Read .gitignore if it exists
            gitignore_path = tmp_path / ".gitignore"
            ignore_patterns = []
            if gitignore_path.exists():
                with open(gitignore_path, 'r') as f:
                    ignore_patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            # Custom ignore function
            def ignore_func(src, names):
                ignored = set()
                for name in names:
                    test_path = Path(src) / name
                    if should_exclude_file(test_path, ignore_patterns):
                        ignored.add(name)
                return ignored
            
            shutil.copytree(tmp_path, comp_dir, ignore=ignore_func)
        else:
            shutil.copytree(tmp_path, comp_dir)
        
        # Create .vendor-info.yaml file for provenance
        vendor_info = {
            "component": name,
            "repo": repo_url,
            "version": version,
            "vendored_at": datetime.utcnow().isoformat() + "Z"
        }
        
        vendor_info_path = comp_dir / ".vendor-info.yaml"
        with open(vendor_info_path, 'w') as f:
            yaml.dump(vendor_info, f, default_flow_style=False, sort_keys=False)
        
        success(f"Vendored {name}@{version} to {comp_dir}")
        return True


def get_vendor_info(component_dir: Path) -> Optional[Dict[str, Any]]:
    """Get vendor information for a component.
    
    Args:
        component_dir: Path to component directory
    
    Returns:
        Vendor info dict or None if not vendored
    """
    vendor_info_path = component_dir / ".vendor-info.yaml"
    if not vendor_info_path.exists():
        return None
    
    try:
        with open(vendor_info_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        error(f"Failed to read vendor info: {e}")
        return None


def is_component_vendored(name: str, manifests_dir: str = "manifests") -> bool:
    """Check if a component is vendored.
    
    Args:
        name: Component name
        manifests_dir: Manifests directory
    
    Returns:
        True if component is vendored, False otherwise
    """
    root = find_meta_repo_root()
    if not root:
        return False
    
    comp_dir = root / "components" / name
    if not comp_dir.exists():
        return False
    
    vendor_info = get_vendor_info(comp_dir)
    return vendor_info is not None


def convert_to_vendored_mode(
    manifests_dir: str = "manifests",
    force: bool = False
) -> bool:
    """Convert from reference mode to vendored mode.
    
    This will:
    1. Check current mode (must be reference)
    2. For each component that's a git repo, vendor it
    3. Update components.yaml to set meta.mode: "vendored"
    
    Args:
        manifests_dir: Manifests directory
        force: Force re-vendoring even if already vendored
    
    Returns:
        True if successful, False otherwise
    """
    if is_vendored_mode(manifests_dir):
        log("Already in vendored mode")
        return True
    
    root = find_meta_repo_root()
    if not root:
        error("Could not find meta-repo root")
        return False
    
    components = get_components(manifests_dir)
    if not components:
        log("No components to convert")
        return True
    
    log("Converting from reference mode to vendored mode...")
    
    # First, update the manifest to vendored mode
    manifest_path = Path(manifests_dir) / "components.yaml"
    if not manifest_path.exists():
        error(f"Manifest not found: {manifest_path}")
        return False
    
    # Read current manifest
    with open(manifest_path, 'r') as f:
        manifest_data = yaml.safe_load(f) or {}
    
    # Update mode
    if "meta" not in manifest_data:
        manifest_data["meta"] = {}
    manifest_data["meta"]["mode"] = "vendored"
    
    # Write updated manifest
    with open(manifest_path, 'w') as f:
        yaml.dump(manifest_data, f, default_flow_style=False, sort_keys=False)
    
    log("Updated components.yaml to vendored mode")
    
    # Now vendor all components
    results = []
    for name, comp in components.items():
        comp_dir = root / "components" / name
        
        # Check if it's a git repo (reference mode)
        if comp_dir.exists() and (comp_dir / ".git").exists():
            log(f"Converting {name} from git repo to vendored source...")
            # Remove the git repo first
            shutil.rmtree(comp_dir)
        
        # Vendor the component
        log(f"Vendoring {name}...")
        success_result = vendor_component(name, comp, manifests_dir, force)
        results.append((name, success_result))
    
    # Summary
    successful = [name for name, ok in results if ok]
    failed = [name for name, ok in results if not ok]
    
    if successful:
        success(f"Successfully converted {len(successful)} components to vendored mode")
    if failed:
        error(f"Failed to convert {len(failed)} components: {', '.join(failed)}")
    
    if failed:
        return False
    
    log("\nConversion complete!")
    log("Next steps:")
    log("  1. Review the vendored code")
    log("  2. Commit changes: git add manifests/components.yaml components/ && git commit -m 'Convert to vendored mode'")
    
    return True


def convert_to_reference_mode(
    manifests_dir: str = "manifests",
    force: bool = False
) -> bool:
    """Convert from vendored mode to reference mode.
    
    This will:
    1. Check current mode (must be vendored)
    2. For each vendored component, read vendor info and clone as git repo
    3. Update components.yaml to set meta.mode: "reference" (or remove mode)
    
    Args:
        manifests_dir: Manifests directory
        force: Force re-cloning even if git repo exists
    
    Returns:
        True if successful, False otherwise
    """
    if not is_vendored_mode(manifests_dir):
        log("Already in reference mode")
        return True
    
    if not git_available():
        error("Git is not available - cannot convert to reference mode")
        return False
    
    root = find_meta_repo_root()
    if not root:
        error("Could not find meta-repo root")
        return False
    
    components = get_components(manifests_dir)
    if not components:
        log("No components to convert")
        return True
    
    log("Converting from vendored mode to reference mode...")
    
    # First, update the manifest to reference mode
    manifest_path = Path(manifests_dir) / "components.yaml"
    if not manifest_path.exists():
        error(f"Manifest not found: {manifest_path}")
        return False
    
    # Read current manifest
    with open(manifest_path, 'r') as f:
        manifest_data = yaml.safe_load(f) or {}
    
    # Update mode (remove or set to reference)
    if "meta" in manifest_data:
        if "mode" in manifest_data["meta"]:
            del manifest_data["meta"]["mode"]
        if not manifest_data["meta"]:  # Remove empty meta dict
            del manifest_data["meta"]
    
    # Write updated manifest
    with open(manifest_path, 'w') as f:
        yaml.dump(manifest_data, f, default_flow_style=False, sort_keys=False)
    
    log("Updated components.yaml to reference mode")
    
    # Now convert each component
    results = []
    for name, comp in components.items():
        comp_dir = root / "components" / name
        
        if not comp_dir.exists():
            error(f"Component {name} not found in components/")
            results.append((name, False))
            continue
        
        vendor_info = get_vendor_info(comp_dir)
        if not vendor_info:
            error(f"Component {name} is not properly vendored (no .vendor-info.yaml)")
            results.append((name, False))
            continue
        
        repo_url = vendor_info.get("repo", comp.get("repo", ""))
        version = vendor_info.get("version", comp.get("version", "latest"))
        
        if not repo_url:
            error(f"No repository URL for {name}")
            results.append((name, False))
            continue
        
        log(f"Converting {name} from vendored source to git repo...")
        
        # Remove vendored source
        shutil.rmtree(comp_dir)
        
        # Clone as git repo
        comp_dir_str = str(comp_dir)
        if not clone_repo(repo_url, comp_dir_str, version):
            error(f"Failed to clone {name}")
            results.append((name, False))
            continue
        
        # Checkout specific version if needed
        if version and version != "latest":
            if not checkout_version(comp_dir_str, version):
                error(f"Failed to checkout version {version} for {name}")
                results.append((name, False))
                continue
        
        log(f"Successfully converted {name} to git repo")
        results.append((name, True))
    
    # Summary
    successful = [name for name, ok in results if ok]
    failed = [name for name, ok in results if not ok]
    
    if successful:
        success(f"Successfully converted {len(successful)} components to reference mode")
    if failed:
        error(f"Failed to convert {len(failed)} components: {', '.join(failed)}")
    
    if failed:
        return False
    
    log("\nConversion complete!")
    log("Next steps:")
    log("  1. Review the git repos")
    log("  2. Commit changes: git add manifests/components.yaml && git commit -m 'Convert to reference mode'")
    
    return True


def convert_to_vendored_for_production(
    env: str = "prod",
    manifests_dir: str = "manifests",
    force: bool = False
) -> bool:
    """Convert to vendored mode specifically for production release.
    
    This workflow:
    1. Uses reference mode in dev/staging (flexible, easy updates)
    2. Converts to vendored mode for production (self-contained, immutable)
    3. Creates production lock file with semantic versions
    
    Args:
        env: Target environment (default: "prod")
        manifests_dir: Manifests directory
        force: Force re-vendoring
    
    Returns:
        True if successful
    """
    from meta.utils.environment_locks import generate_environment_lock_file
    
    log(f"Converting to vendored mode for production release ({env})...")
    
    # Get production environment config (has semantic versions)
    env_config = get_environment_config(env, manifests_dir)
    components = get_components(manifests_dir)
    
    if not components:
        log("No components to convert")
        return True
    
    root = find_meta_repo_root()
    if not root:
        error("Could not find meta-repo root")
        return False
    
    # Update manifest to vendored mode
    manifest_path = Path(manifests_dir) / "components.yaml"
    if not manifest_path.exists():
        error(f"Manifest not found: {manifest_path}")
        return False
    
    with open(manifest_path, 'r') as f:
        manifest_data = yaml.safe_load(f) or {}
    
    # Set vendored mode
    if "meta" not in manifest_data:
        manifest_data["meta"] = {}
    manifest_data["meta"]["mode"] = "vendored"
    
    # Update component versions to production versions in manifest
    if "components" not in manifest_data:
        manifest_data["components"] = {}
    
    for name, comp in components.items():
        if name in env_config:
            # Update version in manifest
            if name in manifest_data["components"]:
                manifest_data["components"][name]["version"] = env_config[name]
            comp["version"] = env_config[name]  # Use production version
    
    with open(manifest_path, 'w') as f:
        yaml.dump(manifest_data, f, default_flow_style=False, sort_keys=False)
    
    log(f"Updated components.yaml with production versions and vendored mode")
    
    # Vendor all components at production versions
    results = []
    for name, comp in components.items():
        # Use production version from environment config
        prod_version = env_config.get(name, comp.get("version", "latest"))
        comp["version"] = prod_version
        
        comp_dir = root / "components" / name
        
        # Remove existing (git repo or old vendored)
        if comp_dir.exists():
            shutil.rmtree(comp_dir)
        
        log(f"Vendoring {name}@{prod_version} for production...")
        success_result = vendor_component(name, comp, manifests_dir, force)
        results.append((name, success_result))
    
    # Generate production lock file
    log(f"Generating production lock file for {env}...")
    if not generate_environment_lock_file(env, manifests_dir):
        error("Failed to generate production lock file")
        return False
    
    # Summary
    successful = [name for name, ok in results if ok]
    failed = [name for name, ok in results if not ok]
    
    if successful:
        success(f"Successfully converted {len(successful)} components to vendored mode for production")
    if failed:
        error(f"Failed to convert {len(failed)} components: {', '.join(failed)}")
    
    if failed:
        return False
    
    log("\n✅ Production release ready!")
    log("Next steps:")
    log("  1. Review vendored components and lock file")
    log("  2. Commit: git add manifests/ components/ && git commit -m 'Production release: Convert to vendored mode'")
    log("  3. Tag release: git tag -a v1.0.0 -m 'Production release v1.0.0'")
    
    return True


# Enhanced conversion functions with new features

def convert_to_vendored_mode_enhanced(
    manifests_dir: str = "manifests",
    force: bool = False,
    dry_run: bool = False,
    continue_on_error: bool = False,
    check_secrets: bool = True,
    fail_on_secrets: bool = False,
    create_backup: bool = True,
    atomic: bool = True,
    respect_gitignore: bool = True,
    resume: bool = False,
    checkpoint_id: Optional[str] = None,
    changeset_id: Optional[str] = None
) -> Tuple[bool, Dict[str, Any]]:
    """Enhanced conversion to vendored mode with all safety features.
    
    Args:
        manifests_dir: Manifests directory
        force: Force re-vendoring even if already vendored
        dry_run: Preview changes without making them
        continue_on_error: Continue converting other components if one fails
        check_secrets: Check for secrets during vendor
        fail_on_secrets: Fail if secrets are detected
        create_backup: Create backup before conversion
        atomic: Use atomic transaction (all-or-nothing)
        respect_gitignore: Respect .gitignore patterns
        resume: Resume from checkpoint
        checkpoint_id: Specific checkpoint ID to resume from
        changeset_id: Changeset ID to associate with conversion
    
    Returns:
        Tuple of (success, results_dict)
    """
    from meta.utils.vendor_validation import validate_conversion_readiness
    from meta.utils.vendor_backup import create_backup
    from meta.utils.vendor_transaction import atomic_conversion, create_transaction
    from meta.utils.changeset import get_current_changeset, load_changeset
    
    results = {
        'successful': [],
        'failed': [],
        'skipped': [],
        'errors': [],
        'checkpoint_id': None,
        'changeset_id': changeset_id
    }
    
    # Resume from checkpoint if requested
    checkpoint = None
    if resume:
        if checkpoint_id:
            checkpoint = load_checkpoint(checkpoint_id)
        else:
            checkpoint = get_latest_checkpoint()
        
        if checkpoint:
            log(f"Resuming from checkpoint: {checkpoint.checkpoint_id}")
            results['checkpoint_id'] = checkpoint.checkpoint_id
        else:
            warning("No checkpoint found, starting fresh conversion")
            resume = False
    
    # Create checkpoint if not resuming
    if not resume:
        checkpoint = create_checkpoint("vendored", manifests_dir)
        results['checkpoint_id'] = checkpoint.checkpoint_id
        log(f"Created checkpoint: {checkpoint.checkpoint_id}")
    
    # Get or create changeset
    if changeset_id:
        changeset = load_changeset(changeset_id)
        if not changeset:
            warning(f"Changeset {changeset_id} not found, continuing without changeset")
            changeset = None
    else:
        # Try to get current changeset
        changeset = get_current_changeset()
        if changeset:
            results['changeset_id'] = changeset.id
            log(f"Using changeset: {changeset.id}")
    
    # Pre-conversion validation (skip if resuming)
    if not resume:
        log("Running pre-conversion validation...")
        is_valid, validation_errors, validation_details = validate_conversion_readiness(
            "vendored",
            manifests_dir,
            check_secrets=check_secrets
        )
        
        if not is_valid:
            error("Pre-conversion validation failed:")
            for err in validation_errors:
                error(f"  - {err}")
            results['errors'].extend(validation_errors)
            if not continue_on_error:
                return False, results
    else:
        validation_details = {'dependencies': {'conversion_order': checkpoint.pending_components}}
    
    # Dry-run mode
    if dry_run:
        log("DRY-RUN MODE: Previewing changes...")
        components = get_components(manifests_dir)
        dep_order = validation_details.get('dependencies', {}).get('conversion_order', list(components.keys()))
        
        log(f"Would convert {len(components)} components in this order:")
        for name in dep_order:
            comp = components[name]
            log(f"  - {name}@{comp.get('version', 'latest')} from {comp.get('repo', 'unknown')}")
        
        if create_backup:
            log("  Would create backup before conversion")
        if atomic:
            log("  Would use atomic transaction")
        
        return True, {'dry_run': True, 'components': dep_order}
    
    # Create backup
    backup_path = None
    if create_backup:
        log("Creating backup...")
        backup_path = create_backup(include_components=True)
        if not backup_path:
            error("Failed to create backup")
            if not continue_on_error:
                return False, results
    
    # Atomic conversion wrapper
    def do_conversion():
        return convert_to_vendored_mode_internal(
            manifests_dir=manifests_dir,
            force=force,
            continue_on_error=continue_on_error,
            check_secrets=check_secrets,
            fail_on_secrets=fail_on_secrets,
            respect_gitignore=respect_gitignore,
            results=results,
            checkpoint=checkpoint,
            changeset=changeset
        )
    
    if atomic and not resume:
        log("Executing atomic conversion...")
        success_flag = atomic_conversion(
            do_conversion,
            create_checkpoint=False  # Already created backup
        )
    else:
        log("Executing conversion...")
        success_flag = do_conversion()
    
    # Cleanup checkpoint on success
    if success_flag and checkpoint:
        cleanup_checkpoint(checkpoint.checkpoint_id)
        log(f"Cleaned up checkpoint: {checkpoint.checkpoint_id}")
    
    return success_flag, results


def convert_to_vendored_mode_internal(
    manifests_dir: str = "manifests",
    force: bool = False,
    continue_on_error: bool = False,
    check_secrets: bool = True,
    fail_on_secrets: bool = False,
    respect_gitignore: bool = True,
    results: Optional[Dict[str, Any]] = None,
    checkpoint: Optional[Any] = None,
    changeset: Optional[Any] = None
) -> bool:
    """Internal conversion function (used by enhanced version)."""
    if results is None:
        results = {'successful': [], 'failed': [], 'skipped': [], 'errors': []}
    
    if is_vendored_mode(manifests_dir):
        log("Already in vendored mode")
        return True
    
    root = find_meta_repo_root()
    if not root:
        error("Could not find meta-repo root")
        return False
    
    components = get_components(manifests_dir)
    if not components:
        log("No components to convert")
        return True
    
    # Get dependency order
    if checkpoint:
        # Use pending components from checkpoint
        dep_order = checkpoint.pending_components
        log(f"Resuming conversion: {len(dep_order)} components remaining")
    else:
        dep_order = get_dependency_order(components)
        log(f"Converting {len(components)} components in dependency order...")
    
    # Update manifest first
    manifest_path = Path(manifests_dir) / "components.yaml"
    if not manifest_path.exists():
        error(f"Manifest not found: {manifest_path}")
        return False
    
    with open(manifest_path, 'r') as f:
        manifest_data = yaml.safe_load(f) or {}
    
    if "meta" not in manifest_data:
        manifest_data["meta"] = {}
    manifest_data["meta"]["mode"] = "vendored"
    
    with open(manifest_path, 'w') as f:
        yaml.dump(manifest_data, f, default_flow_style=False, sort_keys=False)
    
    log("Updated components.yaml to vendored mode")
    
    # Convert components in dependency order
    all_success = True
    for name in dep_order:
        # Skip if already completed (when resuming)
        if checkpoint and checkpoint.is_completed(name):
            log(f"Skipping {name} (already completed)")
            results['skipped'].append(name)
            continue
        
        comp = components[name]
        comp_dir = root / "components" / name
        
        # Check if it's a git repo (reference mode)
        if comp_dir.exists() and (comp_dir / ".git").exists():
            log(f"Converting {name} from git repo to vendored source...")
            shutil.rmtree(comp_dir)
        
        # Vendor the component
        log(f"Vendoring {name}...")
        success_result = vendor_component(
            name, comp, manifests_dir, force,
            check_secrets=check_secrets,
            fail_on_secrets=fail_on_secrets,
            respect_gitignore=respect_gitignore
        )
        
        if success_result:
            results['successful'].append(name)
            if checkpoint:
                checkpoint.mark_completed(name)
            
            # Record in changeset if available
            if changeset:
                from meta.utils.git import get_commit_sha
                comp_dir = root / "components" / name
                if comp_dir.exists():
                    commit_sha = get_commit_sha(str(root))  # Meta-repo commit
                    changeset.add_repo_commit(
                        repo_name=name,
                        repo_url=comp.get("repo", ""),
                        commit_sha=commit_sha or "pending",
                        branch="main",
                        message=f"Vendor {name}@{comp.get('version', 'latest')}"
                    )
        else:
            results['failed'].append(name)
            if checkpoint:
                checkpoint.mark_failed(name)
            all_success = False
            if not continue_on_error:
                error(f"Failed to vendor {name}, aborting")
                return False
    
    # Save changeset if available
    if changeset:
        from meta.utils.changeset import save_changeset
        save_changeset(changeset)
    
    # Summary
    if results['successful']:
        success(f"Successfully converted {len(results['successful'])} components to vendored mode")
    if results['failed']:
        error(f"Failed to convert {len(results['failed'])} components: {', '.join(results['failed'])}")
    
    return all_success


def verify_conversion(
    manifests_dir: str = "manifests",
    check_integrity: bool = True
) -> Tuple[bool, Dict[str, Any]]:
    """Verify that a conversion was successful.
    
    Args:
        manifests_dir: Manifests directory
        check_integrity: Check file integrity
    
    Returns:
        Tuple of (is_valid, verification_details)
    """
    results = {
        'valid': True,
        'components_checked': 0,
        'components_valid': 0,
        'components_invalid': 0,
        'errors': []
    }
    
    if not is_vendored_mode(manifests_dir):
        results['valid'] = False
        results['errors'].append("Not in vendored mode")
        return False, results
    
    root = find_meta_repo_root()
    if not root:
        results['valid'] = False
        results['errors'].append("Could not find meta-repo root")
        return False, results
    
    components = get_components(manifests_dir)
    
    for name, comp in components.items():
        results['components_checked'] += 1
        comp_dir = root / "components" / name
        
        if not comp_dir.exists():
            results['valid'] = False
            results['components_invalid'] += 1
            results['errors'].append(f"Component {name} directory not found")
            continue
        
        vendor_info = get_vendor_info(comp_dir)
        if not vendor_info:
            results['valid'] = False
            results['components_invalid'] += 1
            results['errors'].append(f"Component {name} missing .vendor-info.yaml")
            continue
        
        # Check version matches
        expected_version = comp.get("version", "latest")
        actual_version = vendor_info.get("version", "unknown")
        if expected_version != "latest" and expected_version != actual_version:
            results['valid'] = False
            results['components_invalid'] += 1
            results['errors'].append(f"Component {name} version mismatch: expected {expected_version}, got {actual_version}")
            continue
        
        results['components_valid'] += 1
    
    return results['valid'], results

