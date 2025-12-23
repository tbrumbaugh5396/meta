"""Vendoring utilities for Linus-safe materialization."""

import shutil
import subprocess
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from meta.utils.logger import log, error, success
from meta.utils.git import git_available, clone_repo, checkout_version
from meta.utils.manifest import get_components, find_meta_repo_root, load_yaml, get_environment_config


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
    force: bool = False
) -> bool:
    """Vendor a component by copying its source into meta-repo.
    
    This creates a Linus-safe materialized state where the meta-repo
    contains actual source code, not references.
    
    Args:
        name: Component name
        comp: Component configuration from manifest
        manifests_dir: Manifests directory
        force: Force re-import even if already vendored
    
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
        
        # Clone repository
        try:
            subprocess.run(
                ["git", "clone", repo_url, str(tmp_path)],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            error(f"Failed to clone {repo_url}: {e.stderr}")
            return False
        
        # Checkout specific version
        if version and version != "latest":
            try:
                subprocess.run(
                    ["git", "-C", str(tmp_path), "checkout", version],
                    check=True,
                    capture_output=True,
                    text=True
                )
                log(f"Checked out version {version}")
            except subprocess.CalledProcessError as e:
                error(f"Failed to checkout version {version}: {e.stderr}")
                return False
        
        # Remove .git directory (we don't want git history)
        git_dir = tmp_path / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir)
        
        # Copy source to components directory
        if comp_dir.exists():
            shutil.rmtree(comp_dir)
        
        comp_dir.parent.mkdir(parents=True, exist_ok=True)
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

