"""Rollback utilities for reverting to previous states."""

import yaml
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from meta.utils.logger import log, success, error
from meta.utils.manifest import get_components
from meta.utils.git import checkout_version, get_commit_sha, get_current_version
from meta.utils.lock import load_lock_file, get_locked_components
from meta.utils.environment_locks import load_environment_lock_file
from meta.utils.store import query_store, retrieve_from_store


class RollbackTarget:
    """Represents a rollback target."""
    def __init__(self, component: str, version: Optional[str] = None, 
                 commit: Optional[str] = None, lock_file: Optional[str] = None):
        self.component = component
        self.version = version
        self.commit = commit
        self.lock_file = lock_file
    
    def __repr__(self):
        if self.commit:
            return f"{self.component}@{self.commit[:8]}"
        elif self.version:
            return f"{self.component}@{self.version}"
        else:
            return self.component


def find_rollback_targets(component: Optional[str] = None,
                         manifests_dir: str = "manifests") -> List[RollbackTarget]:
    """Find available rollback targets from lock files and Git history."""
    targets = []
    
    if component:
        # Find targets for specific component
        comp_dir = Path(f"components/{component}")
        if comp_dir.exists():
            # Get current version
            current = get_current_version(str(comp_dir))
            if current:
                targets.append(RollbackTarget(component, version=current))
            
            # Get from lock files
            lock_files = [
                "manifests/components.lock.yaml",
                "manifests/components.lock.dev.yaml",
                "manifests/components.lock.staging.yaml",
                "manifests/components.lock.prod.yaml"
            ]
            
            for lock_file in lock_files:
                lock_path = Path(lock_file)
                if lock_path.exists():
                    locked = get_locked_components(lock_file)
                    if component in locked:
                        locked_comp = locked[component]
                        commit = locked_comp.get("commit")
                        version = locked_comp.get("version")
                        if commit:
                            targets.append(RollbackTarget(
                                component,
                                version=version,
                                commit=commit,
                                lock_file=lock_file
                            ))
    else:
        # Find targets for all components
        components = get_components(manifests_dir)
        for comp_name in components.keys():
            comp_targets = find_rollback_targets(comp_name, manifests_dir)
            targets.extend(comp_targets)
    
    # Remove duplicates
    seen = set()
    unique_targets = []
    for target in targets:
        key = (target.component, target.commit or target.version)
        if key not in seen:
            seen.add(key)
            unique_targets.append(target)
    
    return unique_targets


def rollback_component(component: str, target: RollbackTarget,
                      manifests_dir: str = "manifests") -> bool:
    """Rollback a component to a specific target."""
    log(f"Rolling back {component} to {target}")
    
    comp_dir = Path(f"components/{component}")
    if not comp_dir.exists():
        error(f"Component {component} not found")
        return False
    
    # Determine what to checkout
    checkout_ref = None
    if target.commit:
        checkout_ref = target.commit
    elif target.version:
        checkout_ref = target.version
    else:
        error(f"No rollback target specified for {component}")
        return False
    
    # Checkout the target
    if checkout_version(str(comp_dir), checkout_ref):
        success(f"Rolled back {component} to {checkout_ref[:8] if len(checkout_ref) > 8 else checkout_ref}")
        return True
    else:
        error(f"Failed to rollback {component}")
        return False


def rollback_from_lock_file(lock_file: str, component: Optional[str] = None,
                           manifests_dir: str = "manifests") -> bool:
    """Rollback components to versions specified in a lock file."""
    log(f"Rolling back from lock file: {lock_file}")
    
    locked = get_locked_components(lock_file)
    if not locked:
        error(f"Lock file {lock_file} is empty or invalid")
        return False
    
    components_to_rollback = [component] if component else list(locked.keys())
    all_success = True
    
    for comp_name in components_to_rollback:
        if comp_name not in locked:
            error(f"Component {comp_name} not in lock file")
            all_success = False
            continue
        
        locked_comp = locked[comp_name]
        commit = locked_comp.get("commit")
        version = locked_comp.get("version")
        
        target = RollbackTarget(
            component=comp_name,
            version=version,
            commit=commit,
            lock_file=lock_file
        )
        
        if not rollback_component(comp_name, target, manifests_dir):
            all_success = False
    
    return all_success


def rollback_from_store(component: str, content_hash: str,
                       store_dir: str = ".meta-store") -> bool:
    """Rollback component from content-addressed store."""
    log(f"Rolling back {component} from store: {content_hash[:8]}...")
    
    # Query store
    entry = query_store(content_hash, store_dir)
    if not entry:
        error(f"Store entry not found: {content_hash}")
        return False
    
    # Retrieve to component directory
    comp_dir = f"components/{component}"
    if retrieve_from_store(content_hash, comp_dir, store_dir):
        success(f"Rolled back {component} from store")
        return True
    else:
        error(f"Failed to rollback {component} from store")
        return False


def create_rollback_snapshot(components: Optional[List[str]] = None,
                            manifests_dir: str = "manifests",
                            snapshot_file: str = "rollback-snapshot.yaml") -> bool:
    """Create a snapshot of current state for rollback."""
    log("Creating rollback snapshot...")
    
    if not components:
        comps = get_components(manifests_dir)
        components = list(comps.keys())
    
    snapshot = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "components": {}
    }
    
    for comp_name in components:
        comp_dir = Path(f"components/{comp_name}")
        if comp_dir.exists():
            current_version = get_current_version(str(comp_dir))
            current_commit = get_commit_sha(str(comp_dir))
            
            snapshot["components"][comp_name] = {
                "version": current_version,
                "commit": current_commit
            }
    
    snapshot_path = Path(snapshot_file)
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(snapshot_path, 'w') as f:
        yaml.dump(snapshot, f, default_flow_style=False, sort_keys=False)
    
    success(f"Rollback snapshot created: {snapshot_file}")
    return True


