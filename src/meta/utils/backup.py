"""Backup and restore utilities."""

import tarfile
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from meta.utils.logger import log, success, error
from meta.utils.manifest import get_components
from meta.utils.lock import load_lock_file
from meta.utils.config import get_config


def create_backup(output_path: str, components: Optional[List[str]] = None,
                 manifests_dir: str = "manifests",
                 include_store: bool = False,
                 include_cache: bool = False) -> bool:
    """Create a backup of the meta-repo state."""
    log(f"Creating backup: {output_path}")
    
    backup_path = Path(output_path)
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with tarfile.open(output_path, 'w:gz') as tar:
            # Backup manifests
            manifests_path = Path(manifests_dir)
            if manifests_path.exists():
                tar.add(manifests_path, arcname="manifests")
            
            # Backup lock files
            lock_files = list(Path(manifests_dir).glob("*.lock.yaml"))
            for lock_file in lock_files:
                tar.add(lock_file, arcname=f"manifests/{lock_file.name}")
            
            # Backup component states
            components_data = {}
            if components:
                comp_list = components
            else:
                comp_list = list(get_components(manifests_dir).keys())
            
            for comp_name in comp_list:
                comp_path = Path(f"components/{comp_name}")
                if comp_path.exists():
                    # Get component state
                    from meta.utils.git import get_current_version, get_commit_sha
                    components_data[comp_name] = {
                        "version": get_current_version(str(comp_path)),
                        "commit": get_commit_sha(str(comp_path)),
                        "exists": True
                    }
                else:
                    components_data[comp_name] = {"exists": False}
            
            # Save component states
            states_file = Path("backup_states.json")
            with open(states_file, 'w') as f:
                json.dump(components_data, f, indent=2)
            tar.add(states_file, arcname="backup_states.json")
            states_file.unlink()
            
            # Backup config
            config = get_config()
            config_data = config.get_all()
            if config_data:
                config_file = Path("backup_config.json")
                with open(config_file, 'w') as f:
                    json.dump(config_data, f, indent=2)
                tar.add(config_file, arcname="backup_config.json")
                config_file.unlink()
            
            # Backup store (optional)
            if include_store:
                store_path = Path(".meta-store")
                if store_path.exists():
                    tar.add(store_path, arcname=".meta-store")
            
            # Backup cache (optional)
            if include_cache:
                cache_path = Path(".meta-cache")
                if cache_path.exists():
                    tar.add(cache_path, arcname=".meta-cache")
            
            # Backup metadata
            metadata = {
                "created_at": datetime.utcnow().isoformat() + "Z",
                "components": comp_list,
                "include_store": include_store,
                "include_cache": include_cache
            }
            metadata_file = Path("backup_metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            tar.add(metadata_file, arcname="backup_metadata.json")
            metadata_file.unlink()
        
        success(f"Backup created: {output_path}")
        return True
    except Exception as e:
        error(f"Failed to create backup: {e}")
        return False


def restore_backup(backup_path: str, components: Optional[List[str]] = None,
                  manifests_dir: str = "manifests",
                  restore_store: bool = False,
                  restore_cache: bool = False) -> bool:
    """Restore from a backup."""
    log(f"Restoring from backup: {backup_path}")
    
    backup_file = Path(backup_path)
    if not backup_file.exists():
        error(f"Backup file not found: {backup_path}")
        return False
    
    try:
        with tarfile.open(backup_path, 'r:gz') as tar:
            # Extract manifests
            manifests_path = Path(manifests_dir)
            manifests_path.mkdir(parents=True, exist_ok=True)
            
            for member in tar.getmembers():
                if member.name.startswith("manifests/"):
                    tar.extract(member, path=".")
            
            # Read metadata
            try:
                metadata_file = tar.extractfile("backup_metadata.json")
                if metadata_file:
                    metadata = json.load(metadata_file)
                    log(f"Backup created at: {metadata.get('created_at')}")
            except:
                pass
            
            # Read component states
            try:
                states_file = tar.extractfile("backup_states.json")
                if states_file:
                    components_data = json.load(states_file)
                    log(f"Restoring {len(components_data)} component states")
            except:
                pass
            
            # Restore store (optional)
            if restore_store:
                try:
                    tar.extract(".meta-store", path=".")
                except:
                    log("Store not found in backup")
            
            # Restore cache (optional)
            if restore_cache:
                try:
                    tar.extract(".meta-cache", path=".")
                except:
                    log("Cache not found in backup")
        
        success(f"Backup restored from: {backup_path}")
        return True
    except Exception as e:
        error(f"Failed to restore backup: {e}")
        return False


