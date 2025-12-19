"""Run system-level tests."""

import typer
import subprocess
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from meta.utils.logger import log, success, error, table, panel
from meta.utils.manifest import get_components, get_features
from meta.utils.bazel import run_bazel_test, bazel_available
from meta.utils.metrics import get_metrics_collector
import concurrent.futures

app = typer.Typer(help="Run system-level tests")


@app.callback(invoke_without_command=True)
def test(
    ctx: typer.Context,
    env: str = typer.Option("dev", "--env", "-e", help="Environment to test"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Test specific component only"),
    feature: Optional[str] = typer.Option(None, "--feature", "-f", help="Test specific feature only"),
    skip_unit: bool = typer.Option(False, "--skip-unit", help="Skip unit tests"),
    skip_contract: bool = typer.Option(False, "--skip-contract", help="Skip contract tests"),
    skip_e2e: bool = typer.Option(False, "--skip-e2e", help="Skip end-to-end tests"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Watch mode (re-run on changes)"),
    coverage: bool = typer.Option(False, "--coverage", help="Generate coverage reports"),
    parallel: bool = typer.Option(False, "--parallel", "-p", help="Run tests in parallel"),
    jobs: int = typer.Option(4, "--jobs", "-j", help="Number of parallel jobs"),
):
    """Run system-level end-to-end tests."""
    # Only run if no subcommands were invoked
    if ctx.invoked_subcommand is None:
        log(f"Running tests for environment: {env}")
        
        if not bazel_available():
            error("Bazel is not available")
            raise typer.Exit(code=1)
        
        components = get_components(manifests_dir)
        features = get_features(manifests_dir)
        
        all_success = True
        
        # Watch mode
        if watch:
            log("Watch mode enabled - tests will re-run on file changes")
            # In a real implementation, use watchdog or similar
            log("Watch mode not fully implemented - use file watcher library")
        
        # Run component unit tests
        if not skip_unit:
            log("Running component unit tests...")
            components_to_test = [component] if component else list(components.keys())
            
            collector = get_metrics_collector()
            
            def run_test(comp_name: str) -> tuple[str, bool, float]:
                """Run test for a component and return (name, success, duration)."""
                start_time = time.time()
                comp = components.get(comp_name)
                if not comp:
                    return (comp_name, False, 0.0)
                
                success_flag = False
                if comp.get("type") == "bazel":
                    build_target = comp.get("build_target", "")
                    if build_target:
                        test_target = build_target.replace(":all", ":test").replace(":build", ":test")
                        if not test_target.endswith(":test"):
                            test_target = f"{build_target}:test"
                        
                        log(f"Testing component: {comp_name}")
                        success_flag = run_bazel_test(test_target, f"components/{comp_name}")
                
                duration = time.time() - start_time
                collector.record_operation("test", comp_name, duration, success_flag)
                return (comp_name, success_flag, duration)
            
            if parallel and len(components_to_test) > 1:
                # Parallel execution
                log(f"Running {len(components_to_test)} tests in parallel (jobs={jobs})")
                with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
                    results = list(executor.map(run_test, components_to_test))
                
                for comp_name, success_flag, duration in results:
                    if not success_flag:
                        all_success = False
            else:
                # Sequential execution
                for comp_name in components_to_test:
                    _, success_flag, _ = run_test(comp_name)
                    if not success_flag:
                        all_success = False
        
        # Run contract tests
        if not skip_contract:
            log("Running contract tests...")
            # TODO: Implement contract test execution
            log("Contract tests not yet implemented")
        
        # Run feature/end-to-end tests
        if not skip_e2e:
            log("Running end-to-end feature tests...")
            features_to_test = [feature] if feature else list(features.keys())
            
            for feature_name in features_to_test:
                log(f"Testing feature: {feature_name}")
                # TODO: Implement feature test execution
                log(f"Feature tests for {feature_name} not yet implemented")
        
        # Coverage report
        if coverage:
            log("Generating coverage report...")
            # In a real implementation, aggregate coverage from all components
            log("Coverage aggregation not fully implemented")
        
        if all_success:
            success("All tests passed!")
        else:
            error("Some tests failed")
            raise typer.Exit(code=1)

