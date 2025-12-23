"""License compliance commands."""

import typer
from pathlib import Path
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.license_compliance import check_component_licenses, validate_license_policy
from meta.utils.manifest import get_components

app = typer.Typer(help="License compliance")


@app.command()
def check(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Component name"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Check all components"),
    policy_file: Optional[str] = typer.Option(None, "--policy", help="License policy file"),
):
    """Check component license compliance."""
    components = get_components()
    
    policy_path = Path(policy_file) if policy_file else None
    
    if component:
        if component not in components:
            error(f"Component {component} not found")
            raise typer.Exit(code=1)
        
        component_path = Path(f"components/{component}")
        if not component_path.exists():
            error(f"Component directory not found: {component_path}")
            raise typer.Exit(code=1)
        
        result = check_component_licenses(component, component_path, policy_path)
        
        panel(f"License Compliance: {component}", "Licenses")
        log(f"Total packages: {result['total']}")
        log(f"Compliant: {'Yes' if result['compliant'] else 'No'}")
        
        if result["violations"]:
            log("\nViolations:")
            for violation in result["violations"]:
                log(f"  - {violation}")
    
    elif all_components:
        all_results = []
        for comp_name in components.keys():
            comp_path = Path(f"components/{comp_name}")
            if comp_path.exists():
                result = check_component_licenses(comp_name, comp_path, policy_path)
                all_results.append(result)
        
        panel(f"License Compliance: {len(all_results)} component(s)", "Licenses")
        for result in all_results:
            status = "✅" if result["compliant"] else "❌"
            log(f"{status} {result['component']}: {result['total']} package(s)")
    
    else:
        error("Specify --component or --all")
        raise typer.Exit(code=1)


@app.command()
def report(
    output_format: str = typer.Option("json", "--format", "-f", help="Output format (json/markdown)"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Generate license compliance report."""
    log("Generating license compliance report...")
    log("License reporting not fully implemented")
    if output_file:
        log(f"Would write report to: {output_file}")


