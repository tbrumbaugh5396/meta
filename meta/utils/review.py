"""Component review utilities."""

import subprocess
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error, warning
from meta.utils.manifest import get_components
from meta.utils.git import get_current_version
from meta.utils.health import check_component_health
from meta.utils.dependencies import validate_dependencies


def review_component(
    component: str,
    manifests_dir: str = "manifests"
) -> Dict[str, Any]:
    """Review a component for issues."""
    components = get_components(manifests_dir)
    
    if component not in components:
        return {"error": f"Component {component} not found"}
    
    comp = components[component]
    review = {
        "component": component,
        "issues": [],
        "warnings": [],
        "recommendations": []
    }
    
    # Check version
    desired_version = comp.get("version")
    current_version = get_current_version(f"components/{component}")
    
    if current_version and current_version != desired_version:
        review["warnings"].append(
            f"Version mismatch: desired {desired_version}, current {current_version}"
        )
    
    # Check dependencies
    deps = comp.get("dependencies", [])
    for dep in deps:
        if dep not in components:
            review["issues"].append(f"Missing dependency: {dep}")
    
    # Check health
    health = check_component_health(component, manifests_dir=manifests_dir)
    if not health.get("healthy"):
        review["issues"].append("Component health check failed")
    
    # Check for updates
    if not comp.get("auto_update", False):
        review["recommendations"].append("Consider enabling auto-update")
    
    return review


def review_all_components(
    manifests_dir: str = "manifests"
) -> Dict[str, Dict[str, Any]]:
    """Review all components."""
    components = get_components(manifests_dir)
    reviews = {}
    
    for component in components.keys():
        reviews[component] = review_component(component, manifests_dir)
    
    return reviews


def generate_review_report(
    manifests_dir: str = "manifests"
) -> Dict[str, Any]:
    """Generate a comprehensive review report."""
    reviews = review_all_components(manifests_dir)
    
    total_issues = 0
    total_warnings = 0
    total_recommendations = 0
    
    for review in reviews.values():
        total_issues += len(review.get("issues", []))
        total_warnings += len(review.get("warnings", []))
        total_recommendations += len(review.get("recommendations", []))
    
    return {
        "summary": {
            "total_components": len(reviews),
            "total_issues": total_issues,
            "total_warnings": total_warnings,
            "total_recommendations": total_recommendations
        },
        "reviews": reviews
    }


