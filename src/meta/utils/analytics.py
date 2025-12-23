"""Component analytics utilities."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from meta.utils.logger import log, error
from meta.utils.metrics import get_metrics_collector
from meta.utils.manifest import get_components


def get_usage_statistics(component: Optional[str] = None,
                        days: int = 30):
    """Get usage statistics."""
    collector = get_metrics_collector()
    
    if component:
        metrics = collector.get_component_metrics(component, days)
        return {
            "component": component,
            "statistics": metrics
        }
    else:
        metrics = collector.get_all_metrics(days)
        return {
            "all_components": metrics
        }


def get_performance_trends(component: str, days: int = 30):
    """Get performance trends."""
    collector = get_metrics_collector()
    
    # Get metrics over time
    # In a real implementation, this would query time-series data
    metrics = collector.get_component_metrics(component, days)
    
    return {
        "component": component,
        "trends": {
            "avg_duration": metrics.get("avg_duration", 0.0),
            "total_operations": metrics.get("total_operations", 0),
            "success_rate": (
                metrics.get("successful", 0) / metrics.get("total_operations", 1)
                if metrics.get("total_operations", 0) > 0 else 0.0
            )
        }
    }


def get_dependency_analysis(manifests_dir: str = "manifests"):
    """Analyze dependency relationships."""
    components = get_components(manifests_dir)
    
    from meta.utils.dependencies import resolve_transitive_dependencies
    deps = resolve_transitive_dependencies(components)
    
    # Calculate statistics
    dep_counts = {comp: len(deps.get(comp, set())) for comp in components.keys()}
    most_dependent = max(dep_counts.items(), key=lambda x: x[1]) if dep_counts else None
    
    return {
        "total_components": len(components),
        "total_dependencies": sum(dep_counts.values()),
        "avg_dependencies": sum(dep_counts.values()) / len(dep_counts) if dep_counts else 0,
        "most_dependent": most_dependent[0] if most_dependent else None,
        "dependency_counts": dep_counts
    }


def get_health_trends(days: int = 30):
    """Get health trends over time."""
    # In a real implementation, this would query historical health data
    return {
        "period_days": days,
        "trends": "Health trend analysis not fully implemented"
    }

