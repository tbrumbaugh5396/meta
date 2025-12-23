"""Cache management for build artifacts."""

import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from meta.utils.logger import log, success, error
from meta.utils.cache_keys import get_cache_path, compute_component_cache_key, compute_build_cache_key
from meta.utils.remote_cache import RemoteCacheBackend, create_remote_backend


class CacheEntry:
    """Represents a cache entry."""
    def __init__(self, cache_key: str, component: str, created_at: str, 
                 size: int, metadata: Dict[str, Any]):
        self.cache_key = cache_key
        self.component = component
        self.created_at = created_at
        self.size = size
        self.metadata = metadata


def get_cache_dir(cache_dir: str = ".meta-cache") -> Path:
    """Get or create cache directory."""
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    return cache_path


def store_artifact(cache_key: str, source_path: str, component: str, 
                   metadata: Optional[Dict[str, Any]] = None,
                   cache_dir: str = ".meta-cache",
                   remote_backend: Optional[RemoteCacheBackend] = None) -> bool:
    """Store a build artifact in the cache."""
    try:
        cache_path = get_cache_path(cache_key, cache_dir)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        source = Path(source_path)
        if not source.exists():
            error(f"Source path does not exist: {source_path}")
            return False
        
        # Copy artifact to cache
        if source.is_file():
            shutil.copy2(source, cache_path)
        elif source.is_dir():
            shutil.copytree(source, cache_path, dirs_exist_ok=True)
        else:
            error(f"Source path is neither file nor directory: {source_path}")
            return False
        
        # Store metadata
        metadata_file = cache_path.parent / f"{cache_key}.metadata.json"
        metadata_data = {
            "cache_key": cache_key,
            "component": component,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "size": _get_size(cache_path),
            "metadata": metadata or {}
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata_data, f, indent=2)
        
        # Upload to remote if backend provided
        if remote_backend:
            remote_key = f"{component}/{cache_key}"
            if remote_backend.upload(source_path, remote_key):
                log(f"Uploaded to remote cache: {cache_key[:8]}...")
            else:
                log(f"Failed to upload to remote cache (local cache still available)")
        
        log(f"Cached artifact: {cache_key[:8]}... ({component})")
        return True
    except Exception as e:
        error(f"Failed to store artifact: {e}")
        return False


def retrieve_artifact(cache_key: str, target_path: str, 
                     cache_dir: str = ".meta-cache",
                     remote_backend: Optional[RemoteCacheBackend] = None) -> bool:
    """Retrieve a cached artifact."""
    try:
        cache_path = get_cache_path(cache_key, cache_dir)
        
        # Try remote first if backend provided
        if remote_backend and not cache_path.exists():
            remote_key = f"{cache_key.split('/')[0] if '/' in cache_key else 'unknown'}/{cache_key}"
            if remote_backend.exists(remote_key):
                log(f"Downloading from remote cache: {cache_key[:8]}...")
                if remote_backend.download(remote_key, str(cache_path)):
                    # Now proceed with local retrieval
                    pass
                else:
                    return False
        
        if not cache_path.exists():
            return False
        
        target = Path(target_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy from cache
        if cache_path.is_file():
            shutil.copy2(cache_path, target)
        elif cache_path.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(cache_path, target)
        else:
            return False
        
        log(f"Retrieved artifact from cache: {cache_key[:8]}...")
        return True
    except Exception as e:
        error(f"Failed to retrieve artifact: {e}")
        return False


def invalidate_cache(cache_key: Optional[str] = None, component: Optional[str] = None,
                    cache_dir: str = ".meta-cache") -> int:
    """Invalidate cache entries. Returns number of entries invalidated."""
    cache_path = get_cache_dir(cache_dir)
    invalidated = 0
    
    if cache_key:
        # Invalidate specific cache key
        entry_path = get_cache_path(cache_key, cache_dir)
        if entry_path.exists():
            if entry_path.is_file():
                entry_path.unlink()
            elif entry_path.is_dir():
                shutil.rmtree(entry_path)
            invalidated += 1
        
        # Remove metadata
        metadata_file = entry_path.parent / f"{cache_key}.metadata.json"
        if metadata_file.exists():
            metadata_file.unlink()
    elif component:
        # Invalidate all entries for component
        for entry in list_cache_entries(cache_dir):
            if entry.component == component:
                entry_path = get_cache_path(entry.cache_key, cache_dir)
                if entry_path.exists():
                    if entry_path.is_file():
                        entry_path.unlink()
                    elif entry_path.is_dir():
                        shutil.rmtree(entry_path)
                    invalidated += 1
                
                metadata_file = entry_path.parent / f"{entry.cache_key}.metadata.json"
                if metadata_file.exists():
                    metadata_file.unlink()
    else:
        # Invalidate all
        if cache_path.exists():
            shutil.rmtree(cache_path)
            cache_path.mkdir(parents=True, exist_ok=True)
            invalidated = -1  # Special value for "all"
    
    return invalidated


def list_cache_entries(cache_dir: str = ".meta-cache") -> List[CacheEntry]:
    """List all cache entries."""
    cache_path = get_cache_dir(cache_dir)
    entries = []
    
    if not cache_path.exists():
        return entries
    
    # Scan cache directory
    for subdir in cache_path.iterdir():
        if subdir.is_dir():
            for entry_dir in subdir.iterdir():
                if entry_dir.is_dir() or entry_dir.is_file():
                    cache_key = entry_dir.name
                    metadata_file = entry_dir.parent / f"{cache_key}.metadata.json"
                    
                    if metadata_file.exists():
                        try:
                            with open(metadata_file) as f:
                                metadata_data = json.load(f)
                            entries.append(CacheEntry(
                                cache_key=metadata_data["cache_key"],
                                component=metadata_data["component"],
                                created_at=metadata_data["created_at"],
                                size=metadata_data["size"],
                                metadata=metadata_data["metadata"]
                            ))
                        except Exception:
                            pass
    
    return entries


def get_cache_stats(cache_dir: str = ".meta-cache") -> Dict[str, Any]:
    """Get cache statistics."""
    entries = list_cache_entries(cache_dir)
    
    total_size = sum(entry.size for entry in entries)
    components = {}
    
    for entry in entries:
        if entry.component not in components:
            components[entry.component] = {"count": 0, "size": 0}
        components[entry.component]["count"] += 1
        components[entry.component]["size"] += entry.size
    
    return {
        "total_entries": len(entries),
        "total_size": total_size,
        "total_size_mb": total_size / (1024 * 1024),
        "components": components
    }


def _get_size(path: Path) -> int:
    """Get size of file or directory in bytes."""
    if path.is_file():
        return path.stat().st_size
    elif path.is_dir():
        total = 0
        for item in path.rglob("*"):
            if item.is_file():
                total += item.stat().st_size
        return total
    return 0

