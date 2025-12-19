"""Component compliance commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.compliance import generate_compliance_report, export_compliance_report

app = typer.Typer(help="Component compliance")


@app.command()
def report(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Component name"),
    format: str = typer.Option("json", "--format", "-f", help="Output format (json/yaml)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Generate compliance report."""
    report_data = generate_compliance_report(component, manifests_dir)
    
    summary = report_data["summary"]
    panel(
        f"Total: {summary['total']} | "
        f"Compliant: {summary['compliant']} | "
        f"Non-Compliant: {summary['non_compliant']} | "
        f"Warnings: {summary['warnings']}",
        "Compliance Report"
    )
    
    # Show non-compliant components
    non_compliant = []
    for comp_name, comp_report in report_data["components"].items():
        if not comp_report["compliant"]:
            issue_count = len(comp_report.get("issues", []))
            non_compliant.append([comp_name, issue_count])
    
    if non_compliant:
        table(["Component", "Issues"], non_compliant)
    
    # Export if requested
    if output:
        export_compliance_report(report_data, format, output)
    elif format != "json":
        export_compliance_report(report_data, format)


