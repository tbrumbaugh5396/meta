"""Dependency conflict resolution commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.manifest import get_components
from meta.utils.conflicts import detect_conflicts, resolve_conflict, recommend_updates
from meta.utils.semver import compare_versions, satisfies_range

app = typer.Typer(help="Detect and resolve dependency conflicts")


@app.command()
def check(
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Check for dependency conflicts."""
    log("Checking for dependency conflicts...")
    
    conflicts = detect_conflicts(manifests_dir)
    
    if not conflicts:
        success("No conflicts found!")
        return
    
    error(f"Found {len(conflicts)} conflict(s)")
    panel("Conflicts", "Dependency Conflicts")
    
    rows = []
    for conflict in conflicts:
        versions_str = ", ".join([f"{comp}@{ver}" for comp, ver in conflict.conflicting_versions])
        rows.append([
            conflict.component,
            conflict.dependency,
            conflict.required_range,
            versions_str
        ])
    
    table(["Component", "Dependency", "Required", "Conflicting Versions"], rows)
    raise typer.Exit(code=1)


@app.command()
def resolve(
    strategy: str = typer.Option("latest", "--strategy", "-s", help="Resolution strategy: latest, conservative, first, highest"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be resolved without making changes"),
):
    """Resolve dependency conflicts automatically."""
    log(f"Resolving conflicts using strategy: {strategy}")
    
    conflicts = detect_conflicts(manifests_dir)
    
    if not conflicts:
        success("No conflicts to resolve!")
        return
    
    resolutions = []
    for conflict in conflicts:
        resolution = resolve_conflict(conflict, strategy)
        if resolution:
            resolutions.append({
                "conflict": conflict,
                "resolution": resolution
            })
    
    if dry_run:
        panel("Would Resolve", "Dry Run")
        rows = []
        for res in resolutions:
            rows.append([
                res["conflict"].dependency,
                ", ".join([f"{comp}@{ver}" for comp, ver in res["conflict"].conflicting_versions]),
                res["resolution"]
            ])
        table(["Dependency", "Conflicting", "Resolved To"], rows)
        log("Run without --dry-run to apply resolutions")
    else:
        # In a full implementation, we'd update the manifest files
        log("Conflict resolution not yet implemented for manifest updates")
        log("Use --dry-run to see what would be resolved")
        raise typer.Exit(code=1)


@app.command()
def recommend(
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Recommend dependency updates."""
    log("Analyzing dependencies for update recommendations...")
    
    recommendations = recommend_updates(manifests_dir)
    
    if not recommendations:
        success("No recommendations available")
        return
    
    for comp_name, comp_recs in recommendations.items():
        panel(f"{comp_name}", "Recommendations")
        rows = []
        for rec in comp_recs:
            rows.append([
                rec["dependency"],
                rec["current"],
                rec["recommendation"]
            ])
        table(["Dependency", "Current", "Recommendation"], rows)


