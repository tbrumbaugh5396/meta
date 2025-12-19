"""OS monitoring utilities."""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from meta.utils.logger import log, success, error
from meta.utils.os_config import get_os_manifest


class OSMonitoring:
    """OS monitoring system."""
    
    def __init__(self):
        self.metrics_file = Path(".meta/os-metrics.json")
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect OS metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "system": self._collect_system_metrics(),
            "packages": self._collect_package_metrics(),
            "services": self._collect_service_metrics(),
            "resources": self._collect_resource_metrics()
        }
        
        # Save metrics
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return metrics
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics."""
        metrics = {}
        
        # Uptime
        try:
            result = subprocess.run(
                ["uptime"],
                capture_output=True,
                text=True,
                check=True
            )
            metrics["uptime"] = result.stdout.strip()
        except:
            pass
        
        # Load average
        try:
            result = subprocess.run(
                ["cat", "/proc/loadavg"],
                capture_output=True,
                text=True,
                check=True
            )
            load = result.stdout.strip().split()
            metrics["load_avg"] = {
                "1min": load[0],
                "5min": load[1],
                "15min": load[2]
            }
        except:
            pass
        
        return metrics
    
    def _collect_package_metrics(self) -> Dict[str, Any]:
        """Collect package metrics."""
        metrics = {}
        
        # Package count
        try:
            result = subprocess.run(
                ["dpkg-query", "-f", "${Package}\n", "-W"],
                capture_output=True,
                text=True,
                check=True
            )
            metrics["total_packages"] = len(result.stdout.strip().split("\n"))
        except:
            pass
        
        # Outdated packages
        try:
            result = subprocess.run(
                ["apt list --upgradable 2>/dev/null | wc -l"],
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            metrics["upgradable_packages"] = int(result.stdout.strip())
        except:
            pass
        
        return metrics
    
    def _collect_service_metrics(self) -> Dict[str, Any]:
        """Collect service metrics."""
        metrics = {}
        
        try:
            result = subprocess.run(
                ["systemctl", "list-units", "--type=service", "--state=running", "--no-pager", "--no-legend"],
                capture_output=True,
                text=True,
                check=True
            )
            metrics["running_services"] = len(result.stdout.strip().split("\n"))
        except:
            pass
        
        try:
            result = subprocess.run(
                ["systemctl", "list-units", "--type=service", "--state=failed", "--no-pager", "--no-legend"],
                capture_output=True,
                text=True,
                check=True
            )
            metrics["failed_services"] = len(result.stdout.strip().split("\n"))
        except:
            pass
        
        return metrics
    
    def _collect_resource_metrics(self) -> Dict[str, Any]:
        """Collect resource metrics."""
        metrics = {}
        
        # Memory
        try:
            result = subprocess.run(
                ["free", "-m"],
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                mem_line = lines[1].split()
                metrics["memory"] = {
                    "total_mb": mem_line[1],
                    "used_mb": mem_line[2],
                    "free_mb": mem_line[3]
                }
        except:
            pass
        
        # Disk
        try:
            result = subprocess.run(
                ["df", "-h", "/"],
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                disk_line = lines[1].split()
                metrics["disk"] = {
                    "total": disk_line[1],
                    "used": disk_line[2],
                    "available": disk_line[3],
                    "percent": disk_line[4]
                }
        except:
            pass
        
        return metrics
    
    def check_compliance(self, manifest_path: Optional[Path] = None) -> Dict[str, Any]:
        """Check OS compliance with manifest."""
        from meta.utils.os_state import get_os_state_manager
        
        state_manager = get_os_state_manager()
        diff = state_manager.compare_state(manifest_path)
        
        compliance = {
            "compliant": True,
            "issues": []
        }
        
        # Check packages
        if diff.get("packages", {}).get("missing"):
            compliance["compliant"] = False
            compliance["issues"].append(f"Missing packages: {', '.join(diff['packages']['missing'])}")
        
        if diff.get("packages", {}).get("version_mismatch"):
            compliance["compliant"] = False
            compliance["issues"].append("Package version mismatches detected")
        
        # Check services
        if diff.get("services", {}).get("missing"):
            compliance["compliant"] = False
            compliance["issues"].append(f"Missing services: {', '.join(diff['services']['missing'])}")
        
        if diff.get("services", {}).get("mismatch"):
            compliance["compliant"] = False
            compliance["issues"].append("Service configuration mismatches detected")
        
        # Check users
        if diff.get("users", {}).get("missing"):
            compliance["compliant"] = False
            compliance["issues"].append(f"Missing users: {', '.join(diff['users']['missing'])}")
        
        # Check files
        if diff.get("files", {}).get("missing"):
            compliance["compliant"] = False
            compliance["issues"].append(f"Missing files: {', '.join(diff['files']['missing'])}")
        
        return compliance


def get_os_monitoring() -> OSMonitoring:
    """Get OS monitoring instance."""
    return OSMonitoring()


