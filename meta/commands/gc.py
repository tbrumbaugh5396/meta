"""Garbage collection commands."""

import typer
from meta.utils.logger import log, success, error
from meta.utils.gc import collect_store_garbage, collect_cache_garbage, collect_all_garbage

app = typer.Typer(help="Garbage collection for store and cache")


@app.command()
def store(
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    store_dir: str = typer.Option(".meta-store", "--store-dir", help="Store directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be removed without removing"),
):
    """Collect garbage from store (remove unreferenced entries)."""
    removed = collect_store_garbage(manifests_dir, store_dir, dry_run)
    
    if dry_run:
        log(f"Would remove {removed} store entries")
    else:
        success(f"Removed {removed} store entries")


@app.command()
def cache(
    max_age_days: int = typer.Option(30, "--max-age", help="Maximum age in days"),
    cache_dir: str = typer.Option(".meta-cache", "--cache-dir", help="Cache directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be removed without removing"),
):
    """Collect garbage from cache (remove old entries)."""
    removed = collect_cache_garbage(max_age_days, cache_dir, dry_run)
    
    if dry_run:
        log(f"Would remove {removed} cache entries")
    else:
        success(f"Removed {removed} cache entries")


@app.command()
def all(
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    store_dir: str = typer.Option(".meta-store", "--store-dir", help="Store directory"),
    cache_dir: str = typer.Option(".meta-cache", "--cache-dir", help="Cache directory"),
    max_age_days: int = typer.Option(30, "--max-age", help="Maximum cache age in days"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be removed without removing"),
):
    """Collect garbage from both store and cache."""
    results = collect_all_garbage(manifests_dir, store_dir, cache_dir, max_age_days, dry_run)
    
    if dry_run:
        log(f"Would remove {results['store']} store entries and {results['cache']} cache entries")
    else:
        success(f"Removed {results['store']} store entries and {results['cache']} cache entries")


