"""Cache management commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.cache import (
    store_artifact, retrieve_artifact, invalidate_cache,
    list_cache_entries, get_cache_stats
)
from meta.utils.cache_keys import compute_component_cache_key, compute_build_cache_key
from meta.utils.manifest import get_components
from meta.utils.dependencies import resolve_transitive_dependencies
from meta.utils.remote_cache import create_remote_backend

app = typer.Typer(help="Manage build cache")


@app.command()
def build(
    component: str = typer.Argument(..., help="Component name"),
    source: str = typer.Option(..., "--source", "-s", help="Source artifact path"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    cache_dir: str = typer.Option(".meta-cache", "--cache-dir", "-c", help="Cache directory"),
    remote: Optional[str] = typer.Option(None, "--remote", "-r", help="Remote cache URL (s3://bucket or gs://bucket)"),
):
    """Build and cache an artifact."""
    components = get_components(manifests_dir)
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    comp_data = components[component]
    
    # Resolve dependencies
    deps = resolve_transitive_dependencies(component, components)
    
    # Compute cache key
    cache_key = compute_component_cache_key(component, comp_data, deps, manifests_dir)
    
    # Create remote backend if specified
    remote_backend = None
    if remote:
        remote_backend = create_remote_backend(remote)
        if not remote_backend:
            error(f"Failed to create remote backend: {remote}")
            raise typer.Exit(code=1)
    
    log(f"Building and caching {component} (key: {cache_key[:8]}...)")
    
    if store_artifact(cache_key, source, component, cache_dir=cache_dir, remote_backend=remote_backend):
        success(f"Artifact cached: {cache_key[:8]}...")
    else:
        error("Failed to cache artifact")
        raise typer.Exit(code=1)


@app.command()
def get(
    component: str = typer.Argument(..., help="Component name"),
    target: str = typer.Option(..., "--target", "-t", help="Target path to restore artifact"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    cache_dir: str = typer.Option(".meta-cache", "--cache-dir", "-c", help="Cache directory"),
    remote: Optional[str] = typer.Option(None, "--remote", "-r", help="Remote cache URL (s3://bucket or gs://bucket)"),
):
    """Retrieve a cached artifact."""
    components = get_components(manifests_dir)
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    comp_data = components[component]
    
    # Resolve dependencies
    deps = resolve_transitive_dependencies(component, components)
    
    # Compute cache key
    cache_key = compute_component_cache_key(component, comp_data, deps, manifests_dir)
    
    # Create remote backend if specified
    remote_backend = None
    if remote:
        remote_backend = create_remote_backend(remote)
        if not remote_backend:
            error(f"Failed to create remote backend: {remote}")
            raise typer.Exit(code=1)
    
    log(f"Retrieving cached artifact for {component} (key: {cache_key[:8]}...)")
    
    if retrieve_artifact(cache_key, target, cache_dir=cache_dir, remote_backend=remote_backend):
        success(f"Artifact retrieved: {target}")
    else:
        error("Artifact not found in cache")
        raise typer.Exit(code=1)


@app.command()
def invalidate(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Invalidate cache for specific component"),
    all: bool = typer.Option(False, "--all", "-a", help="Invalidate all cache"),
    cache_dir: str = typer.Option(".meta-cache", "--cache-dir", help="Cache directory"),
):
    """Invalidate cache entries."""
    if all:
        log("Invalidating all cache entries...")
        count = invalidate_cache(cache_dir=cache_dir)
        if count == -1:
            success("All cache entries invalidated")
        else:
            success(f"Invalidated {count} cache entries")
    elif component:
        log(f"Invalidating cache for {component}...")
        count = invalidate_cache(component=component, cache_dir=cache_dir)
        success(f"Invalidated {count} cache entries for {component}")
    else:
        error("Specify --component or --all")
        raise typer.Exit(code=1)


@app.command()
def list(
    cache_dir: str = typer.Option(".meta-cache", "--cache-dir", "-c", help="Cache directory"),
):
    """List all cache entries."""
    entries = list_cache_entries(cache_dir)
    
    if not entries:
        log("No cache entries found")
        return
    
    panel("Cache Entries", "Cache")
    rows = []
    for entry in entries:
        size_mb = entry.size / (1024 * 1024)
        rows.append([
            entry.cache_key[:8] + "...",
            entry.component,
            f"{size_mb:.2f} MB",
            entry.created_at[:10]  # Just date
        ])
    
    table(["Key", "Component", "Size", "Created"], rows)


@app.command()
def stats(
    cache_dir: str = typer.Option(".meta-cache", "--cache-dir", "-c", help="Cache directory"),
):
    """Show cache statistics."""
    stats = get_cache_stats(cache_dir)
    
    panel("Cache Statistics", "Cache")
    log(f"Total entries: {stats['total_entries']}")
    log(f"Total size: {stats['total_size_mb']:.2f} MB")
    
    if stats['components']:
        panel("By Component", "Cache")
        rows = []
        for comp, comp_stats in stats['components'].items():
            rows.append([
                comp,
                comp_stats['count'],
                f"{comp_stats['size'] / (1024 * 1024):.2f} MB"
            ])
        table(["Component", "Entries", "Size"], rows)

