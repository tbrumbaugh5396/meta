"""Component migration commands."""

import typer
import json
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.migration import analyze_repo_structure, generate_migration_plan, execute_migration

app = typer.Typer(help="Component migration tools")


@app.command()
def analyze(
    path: str = typer.Argument(..., help="Path to analyze"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output analysis to file (JSON)"),
):
    """Analyze repository structure for migration."""
    log(f"Analyzing repository: {path}")
    
    analysis = analyze_repo_structure(path)
    
    if not analysis:
        return
    
    panel(f"Analysis: {path}", "Migration Analysis")
    
    components = analysis.get("components", [])
    log(f"Found {len(components)} component(s):")
    
    rows = []
    for comp in components:
        valid = "✅" if not comp.get("suggestions") else "⚠️"
        rows.append([
            valid,
            comp["name"],
            comp["type"],
            f"{len(comp.get('suggestions', []))} issue(s)"
        ])
    
    table(["Status", "Name", "Type", "Issues"], rows)
    
    if output:
        with open(output, 'w') as f:
            json.dump(analysis, f, indent=2)
        success(f"Analysis written to: {output}")


@app.command()
def plan(
    source_path: str = typer.Argument(..., help="Source path"),
    target_component: str = typer.Argument(..., help="Target component name"),
    target_dir: str = typer.Option("components", "--target-dir", help="Target directory"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output plan to file (JSON)"),
):
    """Generate migration plan."""
    log(f"Generating migration plan: {source_path} -> {target_component}")
    
    plan = generate_migration_plan(source_path, target_component, target_dir)
    
    if not plan:
        return
    
    panel("Migration Plan", "Plan")
    
    for comp in plan.get("components", []):
        log(f"\nComponent: {comp['name']}")
        log(f"  Source: {comp['source']}")
        log(f"  Target: {comp['target']}")
        log(f"  Actions:")
        for action in comp.get("actions", []):
            log(f"    - {action}")
    
    if output:
        with open(output, 'w') as f:
            json.dump(plan, f, indent=2)
        success(f"Plan written to: {output}")


@app.command()
def execute(
    plan_file: str = typer.Argument(..., help="Migration plan file (JSON)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done without making changes"),
):
    """Execute migration plan."""
    import json
    
    with open(plan_file) as f:
        plan = json.load(f)
    
    if execute_migration(plan, dry_run=dry_run):
        success("Migration completed")
    else:
        error("Migration failed")
        raise typer.Exit(code=1)


