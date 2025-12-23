"""Component dashboard utilities."""

from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.manifest import get_components
from meta.utils.git import get_current_version

# Import health and metrics with error handling
try:
    from meta.utils.health import run_health_checks
    def check_component_health(comp_name, env, manifests_dir, check_build=False, check_tests=False):
        result = run_health_checks(comp_name, env, manifests_dir, check_build, check_tests)
        class HealthResult:
            healthy = result.get("healthy", False) if isinstance(result, dict) else False
        return HealthResult()
except ImportError:
    def check_component_health(*args, **kwargs):
        class HealthResult:
            healthy = False
        return HealthResult()

try:
    from meta.utils.metrics import get_metrics_collector
except ImportError:
    class MetricsCollector:
        def get_component_metrics(self, *args, **kwargs):
            return {}
    def get_metrics_collector():
        return MetricsCollector()


def generate_dashboard(env: Optional[str] = None,
                     manifests_dir: str = "manifests"):
    """Generate dashboard data."""
    components = get_components(manifests_dir)
    collector = get_metrics_collector()
    
    dashboard_data = {
        "components": [],
        "summary": {
            "total": len(components),
            "healthy": 0,
            "unhealthy": 0,
            "not_checked_out": 0
        }
    }
    
    for comp_name, comp_data in components.items():
        comp_path = Path(f"components/{comp_name}")
        exists = comp_path.exists()
        current_version = None
        
        if exists:
            current_version = get_current_version(str(comp_path))
            try:
                health_result = check_component_health(comp_name, env, manifests_dir, check_build=False, check_tests=False)
                health = health_result.healthy if hasattr(health_result, 'healthy') else None
            except:
                health = None
        else:
            health = None
        
        # Get metrics
        metrics = collector.get_component_metrics(comp_name, days=7) if exists else {}
        
        comp_info = {
            "name": comp_name,
            "type": comp_data.get("type", "unknown"),
            "version": comp_data.get("version", "N/A"),
            "current_version": current_version,
            "exists": exists,
            "healthy": health,
            "metrics": metrics
        }
        
        dashboard_data["components"].append(comp_info)
        
        # Update summary
        if not exists:
            dashboard_data["summary"]["not_checked_out"] += 1
        elif health:
            dashboard_data["summary"]["healthy"] += 1
        else:
            dashboard_data["summary"]["unhealthy"] += 1
    
    return dashboard_data


def display_dashboard(dashboard_data: Dict[str, Any]):
    """Display dashboard."""
    summary = dashboard_data["summary"]
    
    panel(f"Dashboard: {summary['total']} components", "Dashboard")
    
    # Summary
    log(f"\nSummary:")
    log(f"  Total: {summary['total']}")
    log(f"  Healthy: {summary['healthy']} ✅")
    log(f"  Unhealthy: {summary['unhealthy']} ❌")
    log(f"  Not Checked Out: {summary['not_checked_out']} ⚠️")
    
    # Component table
    rows = []
    for comp in dashboard_data["components"]:
        status = "✅" if comp["healthy"] else "❌" if comp["exists"] else "⚠️"
        rows.append([
            status,
            comp["name"],
            comp["type"],
            comp["version"],
            comp["current_version"] or "N/A",
            f"{comp['metrics'].get('avg_duration', 0.0):.2f}s" if comp["metrics"] else "N/A"
        ])
    
    table(["Status", "Component", "Type", "Version", "Current", "Avg Duration"], rows)
