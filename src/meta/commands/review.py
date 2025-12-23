"""Component review commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.review import review_component, review_all_components, generate_review_report

app = typer.Typer(help="Component review")


@app.command()
def component(
    component: str = typer.Argument(..., help="Component name"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Review a component."""
    review = review_component(component, manifests_dir)
    
    if "error" in review:
        error(review["error"])
        raise typer.Exit(code=1)
    
    panel(f"Review for {component}", "Component Review")
    
    issues = review.get("issues", [])
    warnings = review.get("warnings", [])
    recommendations = review.get("recommendations", [])
    
    if issues:
        log("\nIssues:")
        for issue in issues:
            error(f"  • {issue}")
    
    if warnings:
        log("\nWarnings:")
        for warning in warnings:
            log(f"  ⚠ {warning}")
    
    if recommendations:
        log("\nRecommendations:")
        for rec in recommendations:
            log(f"  💡 {rec}")
    
    if not issues and not warnings and not recommendations:
        success("No issues found")


@app.command()
def all(
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Review all components."""
    report = generate_review_report(manifests_dir)
    
    summary = report["summary"]
    panel(
        f"Components: {summary['total_components']} | "
        f"Issues: {summary['total_issues']} | "
        f"Warnings: {summary['total_warnings']} | "
        f"Recommendations: {summary['total_recommendations']}",
        "Review Report"
    )
    
    # Show components with issues
    issues_found = []
    for component, review in report["reviews"].items():
        if review.get("issues"):
            issues_found.append([component, len(review.get("issues", []))])
    
    if issues_found:
        table(["Component", "Issues"], issues_found)
    else:
        success("No issues found in any component")


