"""Security scanning commands."""

import typer
from pathlib import Path
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.security_scan import scan_component_security, auto_fix_security
from meta.utils.manifest import get_components

app = typer.Typer(help="Security scanning")


@app.command()
def scan(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Component name"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Scan all components"),
    severity: Optional[str] = typer.Option(None, "--severity", help="Filter by severity (low/moderate/high/critical)"),
):
    """Scan components for security vulnerabilities."""
    components = get_components()
    
    if component:
        if component not in components:
            error(f"Component {component} not found")
            raise typer.Exit(code=1)
        
        component_path = Path(f"components/{component}")
        if not component_path.exists():
            error(f"Component directory not found: {component_path}")
            raise typer.Exit(code=1)
        
        result = scan_component_security(component, component_path, severity)
        
        panel(f"Security Scan: {component}", "Security")
        log(f"Total vulnerabilities: {result['total']}")
        
        if result["vulnerabilities"]:
            rows = []
            for vuln in result["vulnerabilities"]:
                rows.append([
                    vuln.get("package", "unknown"),
                    vuln.get("severity", "unknown"),
                    vuln.get("type", "unknown")
                ])
            table(["Package", "Severity", "Type"], rows)
        else:
            success("No vulnerabilities found")
    
    elif all_components:
        all_results = []
        for comp_name in components.keys():
            comp_path = Path(f"components/{comp_name}")
            if comp_path.exists():
                result = scan_component_security(comp_name, comp_path, severity)
                if result["total"] > 0:
                    all_results.append(result)
        
        if all_results:
            panel(f"Security Scan: {len(all_results)} component(s) with vulnerabilities", "Security")
            for result in all_results:
                log(f"\n{result['component']}: {result['total']} vulnerability(ies)")
        else:
            success("No vulnerabilities found in any component")
    
    else:
        error("Specify --component or --all")
        raise typer.Exit(code=1)


@app.command()
def fix(
    component: str = typer.Argument(..., help="Component name"),
    auto: bool = typer.Option(False, "--auto", help="Automatically fix vulnerabilities"),
):
    """Fix security vulnerabilities."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = Path(f"components/{component}")
    
    if auto_fix_security(component, component_path):
        success(f"Fixed security vulnerabilities for {component}")
    else:
        error("Failed to fix vulnerabilities")
        raise typer.Exit(code=1)


