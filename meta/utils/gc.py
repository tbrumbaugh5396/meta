"""Garbage collection for store and cache."""

import shutil
from pathlib import Path
from typing import List, Set, Dict, Any
from datetime import datetime, timedelta
from meta.utils.logger import log, success, error
from meta.utils.store import list_store_entries
from meta.utils.store import get_store_path
from meta.utils.cache import list_cache_entries
from meta.utils.cache_keys import get_cache_path
from meta.utils.manifest import get_components
from meta.utils.dependencies import resolve_transitive_dependencies


def find_referenced_store_entries(manifests_dir: str = "manifests",
                                 store_dir: str = ".meta-store") -> Set[str]:
    """Find all store entries referenced by current components."""
    components = get_components(manifests_dir)
    referenced = set()
    
    for comp_name, comp_data in components.items():
        comp_dir = Path(f"components/{comp_name}")
        if comp_dir.exists():
            # In a full implementation, we'd compute content hash and check store
            # For now, we'll mark all as potentially referenced
            deps = resolve_transitive_dependencies(comp_name, components)
            # Add component and dependencies to referenced set
            referenced.add(comp_name)
            referenced.update(deps)
    
    return referenced


def collect_store_garbage(manifests_dir: str = "manifests",
                          store_dir: str = ".meta-store",
                          dry_run: bool = False) -> int:
    """Collect garbage from store (remove unreferenced entries)."""
    log("Collecting store garbage...")
    
    referenced = find_referenced_store_entries(manifests_dir, store_dir)
    all_entries = list_store_entries(store_dir)
    
    removed = 0
    for entry in all_entries:
        content_hash = entry.get("content_hash", "")
        component = entry.get("component", "")
        
        # Check if referenced
        if component not in referenced and content_hash:
            store_path = get_store_path(content_hash, store_dir)
            if store_path.exists():
                if dry_run:
                    log(f"Would remove: {content_hash[:8]}... ({component})")
                else:
                    if store_path.is_file():
                        store_path.unlink()
                    elif store_path.is_dir():
                        shutil.rmtree(store_path)
                    
                    # Remove metadata
                    metadata_file = store_path.parent / f"{content_hash}.metadata.json"
                    if metadata_file.exists():
                        metadata_file.unlink()
                    
                    removed += 1
    
    if dry_run:
        log(f"Would remove {removed} store entries")
    else:
        success(f"Removed {removed} store entries")
    
    return removed


def collect_cache_garbage(max_age_days: int = 30,
                          cache_dir: str = ".meta-cache",
                          dry_run: bool = False) -> int:
    """Collect garbage from cache (remove old entries)."""
    log(f"Collecting cache garbage (older than {max_age_days} days)...")
    
    entries = list_cache_entries(cache_dir)
    cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
    
    removed = 0
    for entry in entries:
        try:
            created_at = datetime.fromisoformat(entry.created_at.replace('Z', '+00:00'))
            if created_at < cutoff_date:
                cache_path = get_cache_path(entry.cache_key, cache_dir)
                if cache_path.exists():
                    if dry_run:
                        log(f"Would remove: {entry.cache_key[:8]}... ({entry.component})")
                    else:
                        if cache_path.is_file():
                            cache_path.unlink()
                        elif cache_path.is_dir():
                            shutil.rmtree(cache_path)
                        
                        # Remove metadata
                        metadata_file = cache_path.parent / f"{entry.cache_key}.metadata.json"
                        if metadata_file.exists():
                            metadata_file.unlink()
                        
                        removed += 1
        except Exception:
            pass
    
    if dry_run:
        log(f"Would remove {removed} cache entries")
    else:
        success(f"Removed {removed} cache entries")
    
    return removed


def collect_all_garbage(manifests_dir: str = "manifests",
                        store_dir: str = ".meta-store",
                        cache_dir: str = ".meta-cache",
                        max_age_days: int = 30,
                        dry_run: bool = False) -> Dict[str, int]:
    """Collect garbage from both store and cache."""
    results = {}
    
    results["store"] = collect_store_garbage(manifests_dir, store_dir, dry_run)
    results["cache"] = collect_cache_garbage(max_age_days, cache_dir, dry_run)
    
    return results

