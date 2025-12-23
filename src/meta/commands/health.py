"""Health check commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.health import check_component_health, check_all_components_health, HealthStatus

app = typer.Typer(help="Check component health")


@app.callback(invoke_without_command=True)
def health(
    ctx: typer.Context,
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Check specific component"),
    env: Optional[str] = typer.Option(None, "--env", "-e", help="Environment to check against"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    check_build: bool = typer.Option(False, "--build", help="Check if component builds"),
    check_tests: bool = typer.Option(False, "--tests", help="Check if component tests pass"),
    all: bool = typer.Option(False, "--all", "-a", help="Check all components"),
):
    """Check component health."""
    if ctx.invoked_subcommand is None:
        if all:
            log("Checking health of all components...")
            statuses = check_all_components_health(
                env=env,
                manifests_dir=manifests_dir,
                check_build=check_build,
                check_tests=check_tests
            )
            
            # Display results
            healthy_count = sum(1 for s in statuses if s.healthy)
            total_count = len(statuses)
            
            panel(f"Health Check Results: {healthy_count}/{total_count} healthy", "Health")
            
            rows = []
            for status in statuses:
                checks_str = ", ".join([name for name, passed in status.checks.items() if passed])
                failed_checks = [name for name, passed in status.checks.items() if not passed]
                if failed_checks:
                    checks_str += f" | Failed: {', '.join(failed_checks)}"
                
                health_icon = "✅" if status.healthy else "❌"
                rows.append([
                    f"{health_icon} {status.component}",
                    checks_str or "No checks",
                    f"{len(status.errors)} errors"
                ])
            
            table(["Component", "Checks", "Issues"], rows)
            
            if healthy_count == total_count:
                success("All components are healthy!")
            else:
                error(f"{total_count - healthy_count} components have issues")
                # Show detailed errors
                for status in statuses:
                    if not status.healthy:
                        log(f"\n{status.component}:")
                        for err in status.errors:
                            error(f"  - {err}")
                raise typer.Exit(code=1)
        elif component:
            log(f"Checking health of component: {component}")
            status = check_component_health(
                component,
                env=env,
                manifests_dir=manifests_dir,
                check_build=check_build,
                check_tests=check_tests
            )
            
            # Display results
            health_icon = "✅" if status.healthy else "❌"
            panel(f"{health_icon} {component}", "Health Check")
            
            rows = []
            for check_name, passed in status.checks.items():
                icon = "✅" if passed else "❌"
                rows.append([f"{icon} {check_name}", "Passed" if passed else "Failed"])
            
            table(["Check", "Status"], rows)
            
            if status.errors:
                error("Errors:")
                for err in status.errors:
                    error(f"  - {err}")
            
            if status.warnings:
                log("Warnings:")
                for warn in status.warnings:
                    log(f"  - {warn}")
            
            if status.healthy:
                success(f"{component} is healthy!")
            else:
                error(f"{component} has issues")
                raise typer.Exit(code=1)
        else:
            error("Specify --component or --all")
            raise typer.Exit(code=1)


