"""Validation utilities for vendor conversion operations."""

from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from meta.utils.logger import log, error, warning
from meta.utils.git import git_available
from meta.utils.manifest import get_components, find_meta_repo_root, load_yaml
from meta.utils.dependencies import validate_dependencies, get_dependency_order
from meta.utils.semver import parse_version
from meta.utils.vendor import is_vendored_mode


def validate_prerequisites(manifests_dir: str = "manifests") -> Tuple[bool, List[str]]:
    """Validate prerequisites for vendor conversion.
    
    Args:
        manifests_dir: Manifests directory
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check Git availability
    if not git_available():
        errors.append("Git is not available - required for vendor operations")
    
    # Check manifest exists
    manifest_path = Path(manifests_dir) / "components.yaml"
    if not manifest_path.exists():
        errors.append(f"Manifest not found: {manifest_path}")
        return False, errors
    
    # Check meta-repo root
    root = find_meta_repo_root()
    if not root:
        errors.append("Could not find meta-repo root")
        return False, errors
    
    # Validate manifest structure
    try:
        manifest = load_yaml(str(manifest_path))
        if not isinstance(manifest, dict):
            errors.append("Manifest is not a valid YAML dictionary")
            return False, errors
        
        components = manifest.get("components", {})
        if not isinstance(components, dict):
            errors.append("Components section is not a valid dictionary")
            return False, errors
        
        # Validate each component
        for name, comp in components.items():
            if not isinstance(comp, dict):
                errors.append(f"Component '{name}' is not a valid dictionary")
                continue
            
            # Check required fields
            repo = comp.get("repo")
            if not repo:
                errors.append(f"Component '{name}' missing required field: repo")
            
            version = comp.get("version", "latest")
            if version != "latest" and not parse_version(version):
                errors.append(f"Component '{name}' has invalid version format: {version}")
    
    except Exception as e:
        errors.append(f"Failed to parse manifest: {e}")
        return False, errors
    
    # Validate dependencies
    dep_valid, dep_errors = validate_dependencies(manifests_dir)
    if not dep_valid:
        errors.extend(dep_errors)
    
    return len(errors) == 0, errors


def validate_component_for_vendor(
    component_name: str,
    component_data: Dict[str, Any],
    manifests_dir: str = "manifests"
) -> Tuple[bool, List[str]]:
    """Validate a single component is ready for vendoring.
    
    Args:
        component_name: Name of component
        component_data: Component configuration
        manifests_dir: Manifests directory
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required fields
    repo = component_data.get("repo")
    if not repo:
        errors.append(f"Component '{component_name}' missing required field: repo")
    
    version = component_data.get("version", "latest")
    if version != "latest":
        if not parse_version(version):
            errors.append(f"Component '{component_name}' has invalid version format: {version}")
    
    # Check if repo URL is valid (basic check)
    if repo and not (repo.startswith("http") or repo.startswith("git@") or repo.startswith("ssh://")):
        errors.append(f"Component '{component_name}' has invalid repo URL format: {repo}")
    
    return len(errors) == 0, errors


def validate_conversion_readiness(
    target_mode: str,
    manifests_dir: str = "manifests",
    check_secrets: bool = True
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """Comprehensive validation before conversion.
    
    Args:
        target_mode: Target mode ('vendored' or 'reference')
        manifests_dir: Manifests directory
        check_secrets: Whether to check for secrets
    
    Returns:
        Tuple of (is_valid, list_of_errors, validation_details)
    """
    errors = []
    details = {
        'prerequisites': {},
        'components': {},
        'dependencies': {},
        'secrets': {}
    }
    
    # Validate prerequisites
    log("Validating prerequisites...")
    prereq_valid, prereq_errors = validate_prerequisites(manifests_dir)
    if not prereq_valid:
        errors.extend(prereq_errors)
    details['prerequisites'] = {
        'valid': prereq_valid,
        'errors': prereq_errors
    }
    
    # Check current mode
    current_mode = "vendored" if is_vendored_mode(manifests_dir) else "reference"
    if current_mode == target_mode:
        warning(f"Already in {target_mode} mode")
        details['mode_check'] = {'current': current_mode, 'target': target_mode, 'needs_conversion': False}
    else:
        details['mode_check'] = {'current': current_mode, 'target': target_mode, 'needs_conversion': True}
    
    # Validate components
    log("Validating components...")
    components = get_components(manifests_dir)
    component_errors = {}
    
    for name, comp in components.items():
        comp_valid, comp_errors = validate_component_for_vendor(name, comp, manifests_dir)
        if not comp_valid:
            component_errors[name] = comp_errors
            errors.extend([f"{name}: {e}" for e in comp_errors])
    
    details['components'] = {
        'total': len(components),
        'valid': len(components) - len(component_errors),
        'invalid': len(component_errors),
        'errors': component_errors
    }
    
    # Validate dependencies
    log("Validating dependencies...")
    dep_valid, dep_errors = validate_dependencies(manifests_dir)
    if not dep_valid:
        errors.extend(dep_errors)
    
    dep_order = get_dependency_order(components)
    details['dependencies'] = {
        'valid': dep_valid,
        'errors': dep_errors,
        'conversion_order': dep_order
    }
    
    # Check for secrets (if requested)
    if check_secrets:
        log("Checking for secrets...")
        from meta.utils.secret_detection import scan_directory_for_secrets
        root = find_meta_repo_root()
        if root:
            # Scan components directory if it exists
            components_dir = root / "components"
            if components_dir.exists():
                secret_results = scan_directory_for_secrets(components_dir)
                if secret_results['total_secrets'] > 0:
                    warning(f"Found {secret_results['total_secrets']} potential secrets")
                    details['secrets'] = {
                        'found': secret_results['total_secrets'],
                        'files_scanned': secret_results['total_files_scanned'],
                        'secrets': secret_results['secrets_found'][:10]  # First 10
                    }
                else:
                    details['secrets'] = {
                        'found': 0,
                        'files_scanned': secret_results['total_files_scanned']
                    }
    
    return len(errors) == 0, errors, details

