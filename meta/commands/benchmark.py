"""Performance benchmarking commands."""

import typer
from pathlib import Path
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.benchmark import run_benchmark, compare_benchmarks, get_performance_trends
from meta.utils.manifest import get_components
from meta.utils.git import checkout_version

app = typer.Typer(help="Performance benchmarking")


@app.command()
def run(
    component: str = typer.Argument(..., help="Component name"),
    command: Optional[str] = typer.Option(None, "--command", "-c", help="Benchmark command to run"),
):
    """Run performance benchmark for a component."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = Path(f"components/{component}")
    
    if not component_path.exists():
        error(f"Component directory not found: {component_path}")
        raise typer.Exit(code=1)
    
    result = run_benchmark(component, component_path, command)
    
    panel(f"Benchmark Results: {component}", "Performance")
    log(f"Duration: {result['duration']:.2f}s")
    log(f"Success: {'Yes' if result['success'] else 'No'}")


@app.command()
def compare(
    component: str = typer.Argument(..., help="Component name"),
    baseline_version: str = typer.Argument(..., help="Baseline version"),
):
    """Compare benchmark results with baseline."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = Path(f"components/{component}")
    
    # Run baseline benchmark
    checkout_version(str(component_path), baseline_version)
    baseline_result = run_benchmark(component, component_path)
    
    # Run current benchmark
    current_version = get_current_version(str(component_path))
    current_result = run_benchmark(component, component_path)
    
    comparison = compare_benchmarks(baseline_result, current_result)
    
    panel(f"Benchmark Comparison: {component}", "Performance")
    log(f"Baseline ({baseline_version}): {comparison['baseline_duration']:.2f}s")
    log(f"Current ({current_version}): {comparison['current_duration']:.2f}s")
    log(f"Improvement: {comparison['improvement']:.1f}%")
    
    if comparison["regression"]:
        error("Performance regression detected!")
        raise typer.Exit(code=1)


@app.command()
def trends(
    component: str = typer.Argument(..., help="Component name"),
    days: int = typer.Option(30, "--days", "-d", help="Number of days"),
):
    """Show performance trends."""
    trends_data = get_performance_trends(component, days)
    log(f"Performance trends for {component} (last {days} days)")
    log(trends_data.get("trends", "Not available"))


