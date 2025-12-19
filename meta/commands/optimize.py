"""Component optimization commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.optimization import analyze_component, optimize_component, optimize_all_components

app = typer.Typer(help="Component optimization")


@app.command()
def analyze(
    component: Optional[str] = typer.Argument(None, help="Component name (optional)"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Analyze component(s) for optimization."""
    if component:
        analysis = analyze_component(component, manifests_dir)
        
        if "error" in analysis:
            error(analysis["error"])
            raise typer.Exit(code=1)
        
        panel(f"Analysis for {component}", "Optimization Analysis")
        
        optimizations = analysis.get("optimizations", [])
        warnings = analysis.get("warnings", [])
        
        if optimizations:
            log("\nOptimization opportunities:")
            for opt in optimizations:
                log(f"  • {opt}")
        
        if warnings:
            log("\nWarnings:")
            for warn in warnings:
                log(f"  ⚠ {warn}")
        
        if not optimizations and not warnings:
            success("No optimization opportunities found")
    else:
        analyses = optimize_all_components(manifests_dir)
        
        rows = []
        for comp_name, analysis in analyses.items():
            opt_count = len(analysis.get("optimizations", []))
            warn_count = len(analysis.get("warnings", []))
            rows.append([comp_name, opt_count, warn_count])
        
        table(["Component", "Optimizations", "Warnings"], rows)


@app.command()
def apply(
    component: str = typer.Argument(..., help="Component name"),
    auto_fix: bool = typer.Option(False, "--auto-fix", help="Automatically apply fixes"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Optimize a component."""
    if optimize_component(component, auto_fix, manifests_dir):
        success(f"Optimization complete for {component}")
    else:
        error("Optimization failed")
        raise typer.Exit(code=1)


