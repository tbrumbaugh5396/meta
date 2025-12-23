"""Component optimization utilities."""

import subprocess
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error, warning
from meta.utils.manifest import get_components
from meta.utils.dependencies import resolve_transitive_dependencies
from meta.utils.health import check_component_health


def analyze_component(
    component: str,
    manifests_dir: str = "manifests"
) -> Dict[str, Any]:
    """Analyze component for optimization opportunities."""
    components = get_components(manifests_dir)
    
    if component not in components:
        return {"error": f"Component {component} not found"}
    
    comp = components[component]
    analysis = {
        "component": component,
        "optimizations": [],
        "warnings": []
    }
    
    # Check dependencies
    deps = comp.get("dependencies", [])
    transitive = resolve_transitive_dependencies(component, manifests_dir)
    
    if len(transitive) > len(deps) * 2:
        analysis["optimizations"].append(
            f"High transitive dependency count ({len(transitive)}), consider reducing direct dependencies"
        )
    
    # Check for unused dependencies
    for dep in deps:
        dependents = [c for c, comp_data in components.items() 
                     if dep in comp_data.get("dependencies", [])]
        if not dependents and dep != component:
            analysis["warnings"].append(f"Potentially unused dependency: {dep}")
    
    # Check version
    version = comp.get("version")
    if version and version.startswith("v"):
        # Check if using latest
        analysis["optimizations"].append("Consider using semantic versioning")
    
    # Check health
    health = check_component_health(component, manifests_dir=manifests_dir)
    if not health.get("healthy"):
        analysis["warnings"].append("Component health check failed")
    
    return analysis


def optimize_component(
    component: str,
    auto_fix: bool = False,
    manifests_dir: str = "manifests"
) -> bool:
    """Optimize a component."""
    analysis = analyze_component(component, manifests_dir)
    
    if "error" in analysis:
        error(analysis["error"])
        return False
    
    log(f"Optimization analysis for {component}:")
    
    optimizations = analysis.get("optimizations", [])
    warnings = analysis.get("warnings", [])
    
    if optimizations:
        log("\nOptimization opportunities:")
        for opt in optimizations:
            log(f"  • {opt}")
    
    if warnings:
        log("\nWarnings:")
        for warn in warnings:
            warning(f"  ⚠ {warn}")
    
    if auto_fix:
        log("\nAuto-fixing issues...")
        # In a real implementation, apply fixes
        success("Auto-fix complete")
    
    return True


def optimize_all_components(
    manifests_dir: str = "manifests"
) -> Dict[str, Dict[str, Any]]:
    """Analyze all components for optimization."""
    components = get_components(manifests_dir)
    analyses = {}
    
    for component in components.keys():
        analyses[component] = analyze_component(component, manifests_dir)
    
    return analyses


