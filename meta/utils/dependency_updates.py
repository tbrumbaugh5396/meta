"""Automated dependency update utilities."""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error, warning
from meta.utils.manifest import get_components
from meta.utils.packages import detect_package_managers


def check_npm_updates(component_path: Path) -> List[Dict[str, Any]]:
    """Check for npm package updates."""
    try:
        result = subprocess.run(
            ["npm", "outdated", "--json"],
            cwd=component_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            outdated = json.loads(result.stdout) if result.stdout else {}
            updates = []
            for pkg, info in outdated.items():
                updates.append({
                    "package": pkg,
                    "current": info.get("current", "unknown"),
                    "wanted": info.get("wanted", "unknown"),
                    "latest": info.get("latest", "unknown"),
                    "type": "npm"
                })
            return updates
    except Exception as e:
        error(f"Failed to check npm updates: {e}")
    
    return []


def check_pip_updates(component_path: Path) -> List[Dict[str, Any]]:
    """Check for pip package updates."""
    try:
        result = subprocess.run(
            ["pip", "list", "--outdated", "--format=json"],
            cwd=component_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            outdated = json.loads(result.stdout) if result.stdout else []
            updates = []
            for pkg_info in outdated:
                updates.append({
                    "package": pkg_info.get("name", "unknown"),
                    "current": pkg_info.get("version", "unknown"),
                    "latest": pkg_info.get("latest_version", "unknown"),
                    "type": "pip"
                })
            return updates
    except Exception as e:
        error(f"Failed to check pip updates: {e}")
    
    return []


def check_security_updates(component_path: Path) -> List[Dict[str, Any]]:
    """Check for security updates."""
    updates = []
    
    # Check npm audit
    try:
        result = subprocess.run(
            ["npm", "audit", "--json"],
            cwd=component_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            audit_data = json.loads(result.stdout) if result.stdout else {}
            vulnerabilities = audit_data.get("vulnerabilities", {})
            
            for pkg, vuln_info in vulnerabilities.items():
                if isinstance(vuln_info, dict) and vuln_info.get("severity") in ["high", "critical"]:
                    updates.append({
                        "package": pkg,
                        "type": "security",
                        "severity": vuln_info.get("severity", "unknown"),
                        "fix": vuln_info.get("fixAvailable", False)
                    })
    except:
        pass
    
    return updates


def check_component_dependency_updates(component: str,
                                      component_path: Path,
                                      security_only: bool = False) -> List[Dict[str, Any]]:
    """Check for dependency updates in a component."""
    updates = []
    
    if security_only:
        updates.extend(check_security_updates(component_path))
    else:
        package_managers = detect_package_managers(component_path)
        
        if "npm" in package_managers:
            updates.extend(check_npm_updates(component_path))
        
        if "pip" in package_managers:
            updates.extend(check_pip_updates(component_path))
    
    return updates


def auto_update_dependencies(component: str,
                              component_path: Path,
                              security_only: bool = False,
                              create_pr: bool = False) -> bool:
    """Automatically update dependencies."""
    updates = check_component_dependency_updates(component, component_path, security_only)
    
    if not updates:
        log(f"No updates available for {component}")
        return True
    
    log(f"Found {len(updates)} update(s) for {component}")
    
    # Update npm packages
    npm_updates = [u for u in updates if u.get("type") == "npm"]
    if npm_updates:
        try:
            packages = [u["package"] for u in npm_updates]
            result = subprocess.run(
                ["npm", "update"] + packages,
                cwd=component_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                success(f"Updated {len(npm_updates)} npm package(s)")
            else:
                error(f"Failed to update npm packages: {result.stderr}")
        except Exception as e:
            error(f"Failed to update npm packages: {e}")
    
    # Update pip packages
    pip_updates = [u for u in updates if u.get("type") == "pip"]
    if pip_updates:
        try:
            packages = [u["package"] for u in pip_updates]
            result = subprocess.run(
                ["pip", "install", "--upgrade"] + packages,
                cwd=component_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                success(f"Updated {len(pip_updates)} pip package(s)")
            else:
                error(f"Failed to update pip packages: {result.stderr}")
        except Exception as e:
            error(f"Failed to update pip packages: {e}")
    
    # Create PR if requested
    if create_pr:
        log("PR creation not fully implemented - use git workflow")
    
    return True


