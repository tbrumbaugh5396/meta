"""Component comparison commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.compare import compare_components, compare_environments

app = typer.Typer(help="Compare components and environments")


@app.command()
def component(
    component1: str = typer.Argument(..., help="First component"),
    component2: str = typer.Argument(..., help="Second component"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Compare two components."""
    result = compare_components(component1, component2, manifests_dir)
    
    if not result:
        return
    
    panel(f"Comparison: {component1} vs {component2}", "Compare")
    
    comp1 = result["component1"]
    comp2 = result["component2"]
    diffs = result["differences"]
    
    rows = [
        ["Property", component1, component2],
        ["Version", comp1["version"], comp2["version"]],
        ["Current Version", comp1["current_version"] or "N/A", comp2["current_version"] or "N/A"],
        ["Type", comp1["type"], comp2["type"]],
        ["Dependencies", f"{len(comp1['dependencies'])}", f"{len(comp2['dependencies'])}"],
    ]
    
    table(["Property", component1, component2], rows)
    
    if diffs["version"] or diffs["type"] or diffs["dependencies"]:
        log("\nDifferences found:")
        if diffs["version"]:
            log(f"  - Version: {comp1['version']} vs {comp2['version']}")
        if diffs["type"]:
            log(f"  - Type: {comp1['type']} vs {comp2['type']}")
        if diffs["dependencies"]:
            log(f"  - Dependencies differ")


@app.command()
def env(
    env1: str = typer.Argument(..., help="First environment"),
    env2: str = typer.Argument(..., help="Second environment"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Compare two environments."""
    result = compare_environments(env1, env2, manifests_dir)
    
    panel(f"Environment Comparison: {env1} vs {env2}", "Compare")
    
    if result["total_differences"] == 0:
        success("No differences between environments")
        return
    
    log(f"Found {result['total_differences']} difference(s):")
    rows = []
    for diff in result["differences"]:
        rows.append([
            diff["component"],
            diff["env1_version"] or "N/A",
            diff["env2_version"] or "N/A"
        ])
    
    table(["Component", env1, env2], rows)


