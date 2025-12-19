"""Content-addressed store system (Nix-like)."""

import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from meta.utils.logger import log, success, error
from meta.utils.content_hash import compute_build_inputs_hash, compute_build_output_hash
from meta.utils.remote_cache import RemoteCacheBackend, create_remote_backend


def get_store_dir(store_dir: str = ".meta-store") -> Path:
    """Get or create store directory."""
    store_path = Path(store_dir)
    store_path.mkdir(parents=True, exist_ok=True)
    return store_path


def get_store_path(content_hash: str, store_dir: str = ".meta-store") -> Path:
    """Get store path for a content hash."""
    store_path = get_store_dir(store_dir)
    # Use first 2 chars for directory structure
    return store_path / content_hash[:2] / content_hash


def add_to_store(source_path: str, content_hash: str, metadata: Dict[str, Any],
                store_dir: str = ".meta-store",
                remote_backend: Optional[RemoteCacheBackend] = None) -> bool:
    """Add an artifact to the content-addressed store."""
    try:
        store_path = get_store_path(content_hash, store_dir)
        store_path.parent.mkdir(parents=True, exist_ok=True)
        
        source = Path(source_path)
        if not source.exists():
            error(f"Source path does not exist: {source_path}")
            return False
        
        # If already in store with same hash, skip (deduplication)
        if store_path.exists():
            log(f"Artifact already in store: {content_hash[:8]}...")
            return True
        
        # Copy to store
        if source.is_file():
            shutil.copy2(source, store_path)
        elif source.is_dir():
            shutil.copytree(source, store_path)
        else:
            error(f"Source path is neither file nor directory: {source_path}")
            return False
        
        # Store metadata
        metadata_file = store_path.parent / f"{content_hash}.metadata.json"
        metadata_data = {
            "content_hash": content_hash,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "source_path": str(source_path),
            **metadata
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata_data, f, indent=2)
        
        # Upload to remote if backend provided
        if remote_backend:
            remote_key = f"{metadata.get('component', 'unknown')}/{content_hash}"
            if remote_backend.upload(source_path, remote_key):
                log(f"Uploaded to remote store: {content_hash[:8]}...")
            else:
                log(f"Failed to upload to remote store (local store still available)")
        
        log(f"Added to store: {content_hash[:8]}...")
        return True
    except Exception as e:
        error(f"Failed to add to store: {e}")
        return False


def query_store(content_hash: str, store_dir: str = ".meta-store") -> Optional[Dict[str, Any]]:
    """Query store for an artifact by content hash."""
    store_path = get_store_path(content_hash, store_dir)
    
    if not store_path.exists():
        return None
    
    metadata_file = store_path.parent / f"{content_hash}.metadata.json"
    if metadata_file.exists():
        try:
            with open(metadata_file) as f:
                return json.load(f)
        except Exception:
            pass
    
    return {
        "content_hash": content_hash,
        "path": str(store_path),
        "exists": True
    }


def retrieve_from_store(content_hash: str, target_path: str,
                       store_dir: str = ".meta-store",
                       remote_backend: Optional[RemoteCacheBackend] = None) -> bool:
    """Retrieve artifact from store by content hash."""
    store_path = get_store_path(content_hash, store_dir)
    
    # Try remote first if backend provided
    if remote_backend and not store_path.exists():
        # Try to find component name from metadata or use hash
        remote_key = f"unknown/{content_hash}"
        if remote_backend.exists(remote_key):
            log(f"Downloading from remote store: {content_hash[:8]}...")
            if remote_backend.download(remote_key, str(store_path)):
                # Now proceed with local retrieval
                pass
            else:
                return False
    
    if not store_path.exists():
        return False
    
    try:
        target = Path(target_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy from store
        if store_path.is_file():
            shutil.copy2(store_path, target)
        elif store_path.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(store_path, target)
        else:
            return False
        
        log(f"Retrieved from store: {content_hash[:8]}...")
        return True
    except Exception as e:
        error(f"Failed to retrieve from store: {e}")
        return False


def list_store_entries(store_dir: str = ".meta-store") -> List[Dict[str, Any]]:
    """List all entries in the store."""
    store_path = get_store_dir(store_dir)
    entries = []
    
    if not store_path.exists():
        return entries
    
    # Scan store directory
    for subdir in store_path.iterdir():
        if subdir.is_dir():
            for entry_dir in subdir.iterdir():
                if entry_dir.is_dir() or entry_dir.is_file():
                    content_hash = entry_dir.name
                    metadata_file = entry_dir.parent / f"{content_hash}.metadata.json"
                    
                    metadata = {}
                    if metadata_file.exists():
                        try:
                            with open(metadata_file) as f:
                                metadata = json.load(f)
                        except Exception:
                            pass
                    
                    entries.append({
                        "content_hash": content_hash,
                        "path": str(entry_dir),
                        **metadata
                    })
    
    return entries


def get_store_stats(store_dir: str = ".meta-store") -> Dict[str, Any]:
    """Get store statistics."""
    entries = list_store_entries(store_dir)
    
    total_size = 0
    for entry in entries:
        entry_path = Path(entry["path"])
        if entry_path.exists():
            if entry_path.is_file():
                total_size += entry_path.stat().st_size
            elif entry_path.is_dir():
                for item in entry_path.rglob("*"):
                    if item.is_file():
                        total_size += item.stat().st_size
    
    return {
        "total_entries": len(entries),
        "total_size": total_size,
        "total_size_mb": total_size / (1024 * 1024),
        "store_dir": store_dir
    }

