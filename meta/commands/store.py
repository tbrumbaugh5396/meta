"""Content-addressed store management commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.store import (
    add_to_store, query_store, retrieve_from_store,
    list_store_entries, get_store_stats
)
from meta.utils.content_hash import compute_build_inputs_hash, compute_build_output_hash
from meta.utils.manifest import get_components
from meta.utils.dependencies import resolve_transitive_dependencies
from meta.utils.remote_cache import create_remote_backend

app = typer.Typer(help="Manage content-addressed store")


@app.command()
def add(
    component: str = typer.Argument(..., help="Component name"),
    source: str = typer.Option(..., "--source", "-s", help="Source artifact path"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    store_dir: str = typer.Option(".meta-store", "--store-dir", help="Store directory"),
    remote: Optional[str] = typer.Option(None, "--remote", "-r", help="Remote store URL (s3://bucket or gs://bucket)"),
):
    """Add an artifact to the content-addressed store."""
    components = get_components(manifests_dir)
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    comp_data = components[component]
    
    # Resolve dependencies
    deps = resolve_transitive_dependencies(component, components)
    
    # Compute content hash
    content_hash = compute_build_inputs_hash(component, comp_data, deps, 
                                            component_dir=f"components/{component}",
                                            manifests_dir=manifests_dir)
    
    # Also compute output hash
    output_hash = compute_build_output_hash(source)
    
    log(f"Adding {component} to store (hash: {content_hash[:8]}...)")
    
    metadata = {
        "component": component,
        "output_hash": output_hash
    }
    
    # Create remote backend if specified
    remote_backend = None
    if remote:
        remote_backend = create_remote_backend(remote)
        if not remote_backend:
            error(f"Failed to create remote backend: {remote}")
            raise typer.Exit(code=1)
    
    if add_to_store(source, content_hash, metadata, store_dir=store_dir, remote_backend=remote_backend):
        success(f"Added to store: {content_hash[:8]}...")
    else:
        error("Failed to add to store")
        raise typer.Exit(code=1)


@app.command()
def query(
    content_hash: str = typer.Argument(..., help="Content hash to query"),
    store_dir: str = typer.Option(".meta-store", "--store-dir", help="Store directory"),
):
    """Query store for an artifact by content hash."""
    entry = query_store(content_hash, store_dir)
    
    if not entry:
        error(f"Entry not found: {content_hash}")
        raise typer.Exit(code=1)
    
    panel("Store Entry", "Query")
    for key, value in entry.items():
        log(f"  {key}: {value}")


@app.command()
def get(
    content_hash: str = typer.Argument(..., help="Content hash to retrieve"),
    target: str = typer.Option(..., "--target", "-t", help="Target path"),
    store_dir: str = typer.Option(".meta-store", "--store-dir", help="Store directory"),
    remote: Optional[str] = typer.Option(None, "--remote", "-r", help="Remote store URL (s3://bucket or gs://bucket)"),
):
    """Retrieve artifact from store by content hash."""
    # Create remote backend if specified
    remote_backend = None
    if remote:
        remote_backend = create_remote_backend(remote)
        if not remote_backend:
            error(f"Failed to create remote backend: {remote}")
            raise typer.Exit(code=1)
    
    if retrieve_from_store(content_hash, target, store_dir=store_dir, remote_backend=remote_backend):
        success(f"Retrieved: {target}")
    else:
        error("Artifact not found in store")
        raise typer.Exit(code=1)


@app.command()
def list(
    store_dir: str = typer.Option(".meta-store", "--store-dir", help="Store directory"),
):
    """List all entries in the store."""
    entries = list_store_entries(store_dir)
    
    if not entries:
        log("Store is empty")
        return
    
    panel("Store Entries", "Store")
    rows = []
    for entry in entries:
        component = entry.get("component", "unknown")
        created = entry.get("created_at", "")[:10] if entry.get("created_at") else ""
        rows.append([
            entry["content_hash"][:8] + "...",
            component,
            created
        ])
    
    table(["Hash", "Component", "Created"], rows)


@app.command()
def stats(
    store_dir: str = typer.Option(".meta-store", "--store-dir", help="Store directory"),
):
    """Show store statistics."""
    stats = get_store_stats(store_dir)
    
    panel("Store Statistics", "Store")
    log(f"Total entries: {stats['total_entries']}")
    log(f"Total size: {stats['total_size_mb']:.2f} MB")
    log(f"Store directory: {stats['store_dir']}")

