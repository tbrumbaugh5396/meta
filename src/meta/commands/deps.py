"""Dependency management commands."""

import typer
from typing import Optional, List
from pathlib import Path
from meta.utils.logger import log, success, error, table, panel
from meta.utils.manifest import get_components
from meta.utils.package_locks import generate_all_package_locks
from meta.utils.security import scan_all_vulnerabilities
from meta.utils.licenses import check_all_licenses
from meta.utils.dependency_graph import (
    build_component_graph,
    build_package_graph,
    export_graph_dot,
    export_graph_json
)

app = typer.Typer(help="Manage component dependencies")


@app.command()
def lock(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Generate locks for specific component"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Generate locks for all components"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Generate package manager lock files (package-lock.json, requirements.lock, etc.)."""
    if component:
        comp_dir = f"components/{component}"
        if not Path(comp_dir).exists():
            error(f"Component {component} not found")
            raise typer.Exit(code=1)
        
        log(f"Generating package locks for {component}")
        results = generate_all_package_locks(comp_dir)
        
        all_success = all(results.values())
        if all_success:
            success(f"Package locks generated for {component}")
        else:
            error(f"Some package locks failed for {component}")
            raise typer.Exit(code=1)
    elif all_components:
        components = get_components(manifests_dir)
        all_success = True
        
        for comp_name in components.keys():
            comp_dir = f"components/{comp_name}"
            if Path(comp_dir).exists():
                log(f"Generating package locks for {comp_name}")
                results = generate_all_package_locks(comp_dir)
                if not all(results.values()):
                    all_success = False
        
        if all_success:
            success("Package locks generated for all components")
        else:
            error("Some package locks failed")
            raise typer.Exit(code=1)
    else:
        error("Specify --component or --all")
        raise typer.Exit(code=1)


@app.command()
def audit(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Audit specific component"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Audit all components"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Scan dependencies for security vulnerabilities."""
    if component:
        comp_dir = f"components/{component}"
        if not Path(comp_dir).exists():
            error(f"Component {component} not found")
            raise typer.Exit(code=1)
        
        log(f"Scanning vulnerabilities for {component}")
        results = scan_all_vulnerabilities(comp_dir)
        
        has_vulns = False
        for pm, result in results.items():
            vulns = result.get("vulnerabilities", [])
            if vulns:
                has_vulns = True
                panel(f"{pm.upper()} Vulnerabilities", "Security")
                rows = []
                for vuln in vulns:
                    rows.append([
                        vuln.get("package", ""),
                        vuln.get("severity", "unknown"),
                        vuln.get("title", vuln.get("description", ""))[:50]
                    ])
                table(["Package", "Severity", "Description"], rows)
        
        if has_vulns:
            error("Vulnerabilities found!")
            raise typer.Exit(code=1)
        else:
            success("No vulnerabilities found")
    elif all_components:
        components = get_components(manifests_dir)
        all_clean = True
        
        for comp_name in components.keys():
            comp_dir = f"components/{comp_name}"
            if Path(comp_dir).exists():
                log(f"Scanning vulnerabilities for {comp_name}")
                results = scan_all_vulnerabilities(comp_dir)
                
                for pm, result in results.items():
                    vulns = result.get("vulnerabilities", [])
                    if vulns:
                        all_clean = False
                        log(f"  {comp_name} ({pm}): {len(vulns)} vulnerabilities")
        
        if all_clean:
            success("No vulnerabilities found in any component")
        else:
            error("Vulnerabilities found in one or more components")
            raise typer.Exit(code=1)
    else:
        error("Specify --component or --all")
        raise typer.Exit(code=1)


@app.command()
def licenses(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Check licenses for specific component"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Check licenses for all components"),
    allowed: Optional[str] = typer.Option(None, "--allowed", help="Comma-separated list of allowed licenses"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Check dependency licenses for compliance."""
    allowed_licenses = allowed.split(",") if allowed else None
    
    if component:
        comp_dir = f"components/{component}"
        if not Path(comp_dir).exists():
            error(f"Component {component} not found")
            raise typer.Exit(code=1)
        
        log(f"Checking licenses for {component}")
        results = check_all_licenses(comp_dir, allowed_licenses)
        
        has_violations = False
        for pm, result in results.items():
            licenses = result.get("licenses", [])
            violations = result.get("violations", [])
            
            if licenses:
                panel(f"{pm.upper()} Licenses", "Compliance")
                rows = []
                for lic in licenses:
                    rows.append([
                        lic.get("package", ""),
                        lic.get("licenses", ""),
                        lic.get("version", "")
                    ])
                table(["Package", "License", "Version"], rows)
            
            if violations:
                has_violations = True
                panel(f"{pm.upper()} License Violations", "Compliance")
                rows = []
                for viol in violations:
                    rows.append([
                        viol.get("package", ""),
                        viol.get("licenses", "")
                    ])
                table(["Package", "License"], rows)
        
        if has_violations:
            error("License violations found!")
            raise typer.Exit(code=1)
        else:
            success("All licenses compliant")
    elif all_components:
        components = get_components(manifests_dir)
        all_compliant = True
        
        for comp_name in components.keys():
            comp_dir = f"components/{comp_name}"
            if Path(comp_dir).exists():
                log(f"Checking licenses for {comp_name}")
                results = check_all_licenses(comp_dir, allowed_licenses)
                
                for pm, result in results.items():
                    violations = result.get("violations", [])
                    if violations:
                        all_compliant = False
                        log(f"  {comp_name} ({pm}): {len(violations)} violations")
        
        if all_compliant:
            success("All components license-compliant")
        else:
            error("License violations found in one or more components")
            raise typer.Exit(code=1)
    else:
        error("Specify --component or --all")
        raise typer.Exit(code=1)


@app.command()
def graph(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Graph for specific component"),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json or dot"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Generate dependency graph visualization."""
    if component:
        comp_dir = f"components/{component}"
        if not Path(comp_dir).exists():
            error(f"Component {component} not found")
            raise typer.Exit(code=1)
        
        log(f"Generating dependency graph for {component}")
        graphs = build_package_graph(comp_dir)
        
        if not graphs:
            error("No package manager dependencies found")
            raise typer.Exit(code=1)
        
        if output:
            if format == "dot":
                export_graph_dot(graphs, output)
            else:
                export_graph_json(graphs, output)
            success(f"Graph exported to {output}")
        else:
            # Print JSON to stdout
            import json
            print(json.dumps(graphs, indent=2))
    else:
        # Component dependency graph
        log("Generating component dependency graph")
        graph = build_component_graph(manifests_dir)
        
        if output:
            if format == "dot":
                export_graph_dot(graph, output)
            else:
                export_graph_json(graph, output)
            success(f"Graph exported to {output}")
        else:
            # Print JSON to stdout
            import json
            print(json.dumps(graph, indent=2))


