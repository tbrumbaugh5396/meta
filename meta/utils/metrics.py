"""Performance monitoring utilities."""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from meta.utils.logger import log, success, error
from meta.utils.manifest import get_components


METRICS_FILE = ".meta/metrics.json"


class MetricsCollector:
    """Collects performance metrics."""
    
    def __init__(self, metrics_file: str = METRICS_FILE):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.metrics: Dict[str, Any] = self._load_metrics()
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Load metrics from file."""
        if not self.metrics_file.exists():
            return {"operations": []}
        
        try:
            with open(self.metrics_file) as f:
                return json.load(f)
        except:
            return {"operations": []}
    
    def _save_metrics(self):
        """Save metrics to file."""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            error(f"Failed to save metrics: {e}")
    
    def record_operation(self, operation: str, component: Optional[str] = None,
                        duration: float = 0.0, success: bool = True,
                        metadata: Optional[Dict[str, Any]] = None):
        """Record an operation."""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "operation": operation,
            "component": component,
            "duration": duration,
            "success": success,
            "metadata": metadata or {}
        }
        
        if "operations" not in self.metrics:
            self.metrics["operations"] = []
        
        self.metrics["operations"].append(entry)
        
        # Keep only last 1000 operations
        if len(self.metrics["operations"]) > 1000:
            self.metrics["operations"] = self.metrics["operations"][-1000:]
        
        self._save_metrics()
    
    def get_component_metrics(self, component: str, days: int = 7) -> Dict[str, Any]:
        """Get metrics for a component."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff.isoformat() + "Z"
        
        component_ops = [
            op for op in self.metrics.get("operations", [])
            if op.get("component") == component and op.get("timestamp", "") >= cutoff_str
        ]
        
        if not component_ops:
            return {}
        
        durations = [op["duration"] for op in component_ops if op.get("duration")]
        successes = [op for op in component_ops if op.get("success")]
        
        return {
            "total_operations": len(component_ops),
            "successful": len(successes),
            "failed": len(component_ops) - len(successes),
            "avg_duration": sum(durations) / len(durations) if durations else 0.0,
            "min_duration": min(durations) if durations else 0.0,
            "max_duration": max(durations) if durations else 0.0,
        }
    
    def get_all_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get all metrics."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff.isoformat() + "Z"
        
        recent_ops = [
            op for op in self.metrics.get("operations", [])
            if op.get("timestamp", "") >= cutoff_str
        ]
        
        if not recent_ops:
            return {"total_operations": 0}
        
        durations = [op["duration"] for op in recent_ops if op.get("duration")]
        successes = [op for op in recent_ops if op.get("success")]
        
        # Group by component
        by_component: Dict[str, List] = {}
        for op in recent_ops:
            comp = op.get("component", "unknown")
            if comp not in by_component:
                by_component[comp] = []
            by_component[comp].append(op)
        
        component_stats = {}
        for comp, ops in by_component.items():
            comp_durations = [o["duration"] for o in ops if o.get("duration")]
            component_stats[comp] = {
                "operations": len(ops),
                "avg_duration": sum(comp_durations) / len(comp_durations) if comp_durations else 0.0
            }
        
        return {
            "total_operations": len(recent_ops),
            "successful": len(successes),
            "failed": len(recent_ops) - len(successes),
            "avg_duration": sum(durations) / len(durations) if durations else 0.0,
            "by_component": component_stats
        }


def get_metrics_collector() -> MetricsCollector:
    """Get metrics collector instance."""
    return MetricsCollector()


