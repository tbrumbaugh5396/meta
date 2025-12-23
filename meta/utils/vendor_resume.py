"""Conversion resume utilities for recovering from interrupted conversions."""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from meta.utils.logger import log, error, success, warning
from meta.utils.manifest import find_meta_repo_root, get_components


RESUME_DIR = Path(".meta/resume")


class ConversionCheckpoint:
    """Represents a conversion checkpoint for resuming."""
    
    def __init__(
        self,
        checkpoint_id: str,
        target_mode: str,
        manifests_dir: str = "manifests"
    ):
        self.checkpoint_id = checkpoint_id
        self.target_mode = target_mode
        self.manifests_dir = manifests_dir
        self.checkpoint_dir = RESUME_DIR / checkpoint_id
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.completed_components: Set[str] = set()
        self.failed_components: Set[str] = set()
        self.pending_components: List[str] = []
        self.created_at = datetime.utcnow().isoformat() + "Z"
    
    def save(self):
        """Save checkpoint to disk."""
        checkpoint_data = {
            'checkpoint_id': self.checkpoint_id,
            'target_mode': self.target_mode,
            'manifests_dir': self.manifests_dir,
            'created_at': self.created_at,
            'completed_components': list(self.completed_components),
            'failed_components': list(self.failed_components),
            'pending_components': self.pending_components
        }
        
        checkpoint_file = self.checkpoint_dir / "checkpoint.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
    
    def mark_completed(self, component_name: str):
        """Mark a component as completed."""
        self.completed_components.add(component_name)
        if component_name in self.pending_components:
            self.pending_components.remove(component_name)
        if component_name in self.failed_components:
            self.failed_components.remove(component_name)
        self.save()
    
    def mark_failed(self, component_name: str):
        """Mark a component as failed."""
        self.failed_components.add(component_name)
        if component_name in self.pending_components:
            self.pending_components.remove(component_name)
        if component_name in self.completed_components:
            self.completed_components.remove(component_name)
        self.save()
    
    def is_completed(self, component_name: str) -> bool:
        """Check if a component is already completed."""
        return component_name in self.completed_components
    
    def is_failed(self, component_name: str) -> bool:
        """Check if a component previously failed."""
        return component_name in self.failed_components
    
    def get_progress(self) -> Dict[str, Any]:
        """Get conversion progress."""
        total = len(self.completed_components) + len(self.failed_components) + len(self.pending_components)
        return {
            'total': total,
            'completed': len(self.completed_components),
            'failed': len(self.failed_components),
            'pending': len(self.pending_components),
            'progress_percent': (len(self.completed_components) / total * 100) if total > 0 else 0
        }


def create_checkpoint(
    target_mode: str,
    manifests_dir: str = "manifests",
    checkpoint_id: Optional[str] = None
) -> ConversionCheckpoint:
    """Create a new conversion checkpoint.
    
    Args:
        target_mode: Target mode ('vendored' or 'reference')
        manifests_dir: Manifests directory
        checkpoint_id: Optional checkpoint ID (defaults to timestamp)
    
    Returns:
        ConversionCheckpoint instance
    """
    import uuid
    
    if not checkpoint_id:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        checkpoint_id = f"checkpoint_{timestamp}_{str(uuid.uuid4())[:8]}"
    
    checkpoint = ConversionCheckpoint(checkpoint_id, target_mode, manifests_dir)
    
    # Initialize with all components as pending
    components = get_components(manifests_dir)
    root = find_meta_repo_root()
    
    if root:
        # Check which components are already converted
        # Import here to avoid circular import
        from meta.utils.vendor import is_component_vendored
        
        for name in components.keys():
            if target_mode == "vendored":
                if is_component_vendored(name, manifests_dir):
                    checkpoint.completed_components.add(name)
                else:
                    checkpoint.pending_components.append(name)
            else:  # reference mode
                comp_dir = root / "components" / name
                if comp_dir.exists() and (comp_dir / ".git").exists():
                    checkpoint.completed_components.add(name)
                else:
                    checkpoint.pending_components.append(name)
    
    checkpoint.save()
    return checkpoint


def load_checkpoint(checkpoint_id: str) -> Optional[ConversionCheckpoint]:
    """Load an existing checkpoint.
    
    Args:
        checkpoint_id: Checkpoint ID
    
    Returns:
        ConversionCheckpoint instance or None if not found
    """
    checkpoint_dir = RESUME_DIR / checkpoint_id
    checkpoint_file = checkpoint_dir / "checkpoint.json"
    
    if not checkpoint_file.exists():
        return None
    
    try:
        with open(checkpoint_file, 'r') as f:
            data = json.load(f)
        
        checkpoint = ConversionCheckpoint(
            data['checkpoint_id'],
            data['target_mode'],
            data.get('manifests_dir', 'manifests')
        )
        checkpoint.created_at = data.get('created_at', checkpoint.created_at)
        checkpoint.completed_components = set(data.get('completed_components', []))
        checkpoint.failed_components = set(data.get('failed_components', []))
        checkpoint.pending_components = data.get('pending_components', [])
        
        return checkpoint
    except Exception as e:
        error(f"Failed to load checkpoint: {e}")
        return None


def list_checkpoints() -> List[Dict[str, Any]]:
    """List all available checkpoints.
    
    Returns:
        List of checkpoint metadata dictionaries
    """
    if not RESUME_DIR.exists():
        return []
    
    checkpoints = []
    for checkpoint_dir in RESUME_DIR.iterdir():
        if not checkpoint_dir.is_dir():
            continue
        
        checkpoint_file = checkpoint_dir / "checkpoint.json"
        if checkpoint_file.exists():
            try:
                with open(checkpoint_file, 'r') as f:
                    data = json.load(f)
                    data['path'] = str(checkpoint_dir)
                    checkpoints.append(data)
            except Exception as e:
                warning(f"Failed to read checkpoint {checkpoint_dir.name}: {e}")
    
    # Sort by creation time (newest first)
    checkpoints.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return checkpoints


def get_latest_checkpoint() -> Optional[ConversionCheckpoint]:
    """Get the most recent checkpoint.
    
    Returns:
        ConversionCheckpoint instance or None
    """
    checkpoints = list_checkpoints()
    if not checkpoints:
        return None
    
    latest = checkpoints[0]
    return load_checkpoint(latest['checkpoint_id'])


def resume_conversion(
    checkpoint_id: Optional[str] = None,
    skip_completed: bool = True,
    retry_failed: bool = True
) -> Optional[ConversionCheckpoint]:
    """Resume a conversion from a checkpoint.
    
    Args:
        checkpoint_id: Checkpoint ID (defaults to latest)
        skip_completed: Skip already completed components
        retry_failed: Retry previously failed components
    
    Returns:
        ConversionCheckpoint instance or None if not found
    """
    if checkpoint_id:
        checkpoint = load_checkpoint(checkpoint_id)
    else:
        checkpoint = get_latest_checkpoint()
    
    if not checkpoint:
        error("No checkpoint found")
        return None
    
    log(f"Resuming conversion from checkpoint: {checkpoint.checkpoint_id}")
    progress = checkpoint.get_progress()
    log(f"Progress: {progress['completed']}/{progress['total']} completed ({progress['progress_percent']:.1f}%)")
    
    if skip_completed:
        log(f"Skipping {len(checkpoint.completed_components)} already completed components")
    
    if retry_failed:
        log(f"Retrying {len(checkpoint.failed_components)} previously failed components")
        # Move failed components back to pending
        checkpoint.pending_components.extend(checkpoint.failed_components)
        checkpoint.failed_components.clear()
        checkpoint.save()
    
    return checkpoint


def cleanup_checkpoint(checkpoint_id: str):
    """Clean up a checkpoint after successful completion.
    
    Args:
        checkpoint_id: Checkpoint ID
    """
    checkpoint_dir = RESUME_DIR / checkpoint_id
    if checkpoint_dir.exists():
        import shutil
        shutil.rmtree(checkpoint_dir)
        log(f"Cleaned up checkpoint: {checkpoint_id}")

