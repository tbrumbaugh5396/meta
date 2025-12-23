"""Backup and restore utilities for vendor conversions."""

import shutil
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from meta.utils.logger import log, error, success, warning
from meta.utils.manifest import find_meta_repo_root, load_yaml


BACKUP_DIR = Path(".meta/backups")


def create_backup(
    backup_name: Optional[str] = None,
    include_components: bool = True
) -> Optional[Path]:
    """Create a backup of the current meta-repo state.
    
    Args:
        backup_name: Optional name for backup (defaults to timestamp)
        include_components: Whether to backup components directory
    
    Returns:
        Path to backup directory, or None if failed
    """
    root = find_meta_repo_root()
    if not root:
        error("Could not find meta-repo root")
        return None
    
    # Create backup directory
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate backup name
    if not backup_name:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
    
    backup_path = BACKUP_DIR / backup_name
    if backup_path.exists():
        error(f"Backup already exists: {backup_path}")
        return None
    
    backup_path.mkdir(parents=True, exist_ok=True)
    
    log(f"Creating backup: {backup_name}")
    
    # Backup manifests
    manifests_src = root / "manifests"
    manifests_dst = backup_path / "manifests"
    if manifests_src.exists():
        shutil.copytree(manifests_src, manifests_dst)
        log("  ✓ Backed up manifests")
    
    # Backup components (if requested)
    if include_components:
        components_src = root / "components"
        components_dst = backup_path / "components"
        if components_src.exists():
            # For large components, we might want to skip git repos
            # and only backup vendored source
            shutil.copytree(components_src, components_dst, ignore=shutil.ignore_patterns('.git'))
            log("  ✓ Backed up components")
    
    # Create backup metadata
    metadata = {
        'backup_name': backup_name,
        'created_at': datetime.utcnow().isoformat() + "Z",
        'meta_repo_root': str(root),
        'includes_components': include_components,
        'manifests_backed_up': manifests_src.exists(),
        'components_backed_up': include_components and (root / "components").exists()
    }
    
    metadata_path = backup_path / "backup_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    success(f"Backup created: {backup_path}")
    return backup_path


def list_backups() -> List[Dict[str, Any]]:
    """List all available backups.
    
    Returns:
        List of backup metadata dictionaries
    """
    if not BACKUP_DIR.exists():
        return []
    
    backups = []
    for backup_path in BACKUP_DIR.iterdir():
        if not backup_path.is_dir():
            continue
        
        metadata_path = backup_path / "backup_metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    metadata['path'] = str(backup_path)
                    backups.append(metadata)
            except Exception as e:
                warning(f"Failed to read backup metadata for {backup_path}: {e}")
        else:
            # Legacy backup without metadata
            backups.append({
                'backup_name': backup_path.name,
                'path': str(backup_path),
                'created_at': 'unknown'
            })
    
    # Sort by creation time (newest first)
    backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return backups


def restore_backup(
    backup_name: str,
    restore_components: bool = True
) -> bool:
    """Restore from a backup.
    
    Args:
        backup_name: Name of backup to restore
        restore_components: Whether to restore components directory
    
    Returns:
        True if successful, False otherwise
    """
    root = find_meta_repo_root()
    if not root:
        error("Could not find meta-repo root")
        return False
    
    backup_path = BACKUP_DIR / backup_name
    if not backup_path.exists():
        error(f"Backup not found: {backup_path}")
        return False
    
    log(f"Restoring from backup: {backup_name}")
    
    # Read backup metadata
    metadata_path = backup_path / "backup_metadata.json"
    metadata = {}
    if metadata_path.exists():
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        except Exception as e:
            warning(f"Failed to read backup metadata: {e}")
    
    # Restore manifests
    manifests_src = backup_path / "manifests"
    manifests_dst = root / "manifests"
    if manifests_src.exists():
        if manifests_dst.exists():
            shutil.rmtree(manifests_dst)
        shutil.copytree(manifests_src, manifests_dst)
        log("  ✓ Restored manifests")
    
    # Restore components (if requested)
    if restore_components:
        components_src = backup_path / "components"
        components_dst = root / "components"
        if components_src.exists():
            if components_dst.exists():
                shutil.rmtree(components_dst)
            shutil.copytree(components_src, components_dst)
            log("  ✓ Restored components")
    
    success(f"Restored from backup: {backup_name}")
    return True


def get_latest_backup() -> Optional[Dict[str, Any]]:
    """Get the most recent backup.
    
    Returns:
        Backup metadata dictionary or None
    """
    backups = list_backups()
    if not backups:
        return None
    return backups[0]

