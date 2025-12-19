"""Security scanning utilities."""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error, warning
from meta.utils.packages import detect_package_managers


def scan_npm_security(component_path: Path) -> Dict[str, Any]:
    """Scan npm packages for security vulnerabilities."""
    try:
        result = subprocess.run(
            ["npm", "audit", "--json"],
            cwd=component_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            audit_data = json.loads(result.stdout) if result.stdout else {}
            vulnerabilities = audit_data.get("vulnerabilities", {})
            
            # Count by severity
            counts = {"low": 0, "moderate": 0, "high": 0, "critical": 0}
            for vuln in vulnerabilities.values():
                if isinstance(vuln, dict):
                    severity = vuln.get("severity", "unknown")
                    if severity in counts:
                        counts[severity] += 1
            
            return {
                "vulnerabilities": vulnerabilities,
                "counts": counts,
                "total": len(vulnerabilities)
            }
    except Exception as e:
        error(f"Failed to scan npm security: {e}")
    
    return {"vulnerabilities": {}, "counts": {}, "total": 0}


def scan_pip_security(component_path: Path) -> Dict[str, Any]:
    """Scan pip packages for security vulnerabilities."""
    try:
        result = subprocess.run(
            ["pip-audit", "--format=json"],
            cwd=component_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            audit_data = json.loads(result.stdout) if result.stdout else {}
            vulnerabilities = audit_data.get("vulnerabilities", [])
            
            return {
                "vulnerabilities": vulnerabilities,
                "total": len(vulnerabilities)
            }
    except Exception as e:
        # pip-audit might not be installed
        warning(f"pip-audit not available: {e}")
    
    return {"vulnerabilities": [], "total": 0}


def scan_component_security(component: str,
                           component_path: Path,
                           severity: Optional[str] = None) -> Dict[str, Any]:
    """Scan component for security vulnerabilities."""
    package_managers = detect_package_managers(component_path)
    
    all_vulnerabilities = []
    total = 0
    
    if "npm" in package_managers:
        npm_result = scan_npm_security(component_path)
        total += npm_result.get("total", 0)
        if npm_result.get("vulnerabilities"):
            for vuln in npm_result["vulnerabilities"].values():
                if isinstance(vuln, dict):
                    vuln_severity = vuln.get("severity", "unknown")
                    if severity is None or vuln_severity == severity:
                        all_vulnerabilities.append({
                            "package": vuln.get("name", "unknown"),
                            "severity": vuln_severity,
                            "type": "npm"
                        })
    
    if "pip" in package_managers:
        pip_result = scan_pip_security(component_path)
        total += pip_result.get("total", 0)
        if pip_result.get("vulnerabilities"):
            for vuln in pip_result["vulnerabilities"]:
                vuln_severity = vuln.get("severity", "unknown")
                if severity is None or vuln_severity == severity:
                    all_vulnerabilities.append({
                        "package": vuln.get("name", "unknown"),
                        "severity": vuln_severity,
                        "type": "pip"
                    })
    
    return {
        "component": component,
        "vulnerabilities": all_vulnerabilities,
        "total": total
    }


def auto_fix_security(component: str,
                     component_path: Path) -> bool:
    """Automatically fix security vulnerabilities."""
    package_managers = detect_package_managers(component_path)
    
    if "npm" in package_managers:
        try:
            result = subprocess.run(
                ["npm", "audit", "fix"],
                cwd=component_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                success("Fixed npm security vulnerabilities")
            else:
                warning("Some npm vulnerabilities could not be auto-fixed")
        except Exception as e:
            error(f"Failed to fix npm vulnerabilities: {e}")
    
    return True


