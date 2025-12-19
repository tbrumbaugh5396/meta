"""Security vulnerability scanning for dependencies."""

import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, error, success, warning


def scan_npm_vulnerabilities(component_dir: str) -> Dict[str, Any]:
    """Scan npm dependencies for vulnerabilities."""
    comp_path = Path(component_dir)
    package_json = comp_path / "package.json"
    
    if not package_json.exists():
        return {"package_manager": "npm", "vulnerabilities": [], "error": "No package.json found"}
    
    if not shutil.which("npm"):
        return {"package_manager": "npm", "vulnerabilities": [], "error": "npm not available"}
    
    log(f"Scanning npm vulnerabilities for {component_dir}")
    try:
        result = subprocess.run(
            ["npm", "audit", "--json"],
            cwd=component_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0 and result.returncode != 1:  # 1 means vulnerabilities found
            return {"package_manager": "npm", "vulnerabilities": [], "error": result.stderr}
        
        audit_data = json.loads(result.stdout)
        vulnerabilities = []
        
        if "vulnerabilities" in audit_data:
            for pkg_name, vuln_data in audit_data["vulnerabilities"].items():
                if isinstance(vuln_data, dict) and "vulnerabilities" in vuln_data:
                    for vuln in vuln_data["vulnerabilities"]:
                        vulnerabilities.append({
                            "package": pkg_name,
                            "severity": vuln.get("severity", "unknown"),
                            "title": vuln.get("title", ""),
                            "url": vuln.get("url", ""),
                            "patched_versions": vuln.get("patched_versions", "")
                        })
        
        return {
            "package_manager": "npm",
            "vulnerabilities": vulnerabilities,
            "summary": audit_data.get("metadata", {}).get("vulnerabilities", {})
        }
    except Exception as e:
        return {"package_manager": "npm", "vulnerabilities": [], "error": str(e)}


def scan_pip_vulnerabilities(component_dir: str) -> Dict[str, Any]:
    """Scan pip dependencies for vulnerabilities."""
    comp_path = Path(component_dir)
    requirements_txt = comp_path / "requirements.txt"
    
    if not requirements_txt.exists():
        return {"package_manager": "pip", "vulnerabilities": [], "error": "No requirements.txt found"}
    
    # Try pip-audit if available
    if shutil.which("pip-audit"):
        log(f"Scanning pip vulnerabilities with pip-audit for {component_dir}")
        try:
            result = subprocess.run(
                ["pip-audit", "--format", "json"],
                cwd=component_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                audit_data = json.loads(result.stdout)
                vulnerabilities = []
                
                for vuln in audit_data.get("vulnerabilities", []):
                    vulnerabilities.append({
                        "package": vuln.get("name", ""),
                        "installed_version": vuln.get("installed_version", ""),
                        "vulnerability": vuln.get("vulnerability", {}).get("id", ""),
                        "severity": vuln.get("vulnerability", {}).get("severity", "unknown"),
                        "description": vuln.get("vulnerability", {}).get("description", "")
                    })
                
                return {
                    "package_manager": "pip",
                    "vulnerabilities": vulnerabilities,
                    "scanner": "pip-audit"
                }
        except Exception as e:
            log(f"pip-audit failed: {e}, trying alternative method")
    
    # Fallback: check if safety is available
    if shutil.which("safety"):
        log(f"Scanning pip vulnerabilities with safety for {component_dir}")
        try:
            result = subprocess.run(
                ["safety", "check", "--json"],
                cwd=component_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 or result.returncode == 255:  # 255 means vulnerabilities found
                audit_data = json.loads(result.stdout)
                vulnerabilities = []
                
                for vuln in audit_data:
                    vulnerabilities.append({
                        "package": vuln.get("package", ""),
                        "installed_version": vuln.get("installed_version", ""),
                        "vulnerability": vuln.get("vulnerability", ""),
                        "severity": vuln.get("severity", "unknown"),
                        "description": vuln.get("description", "")
                    })
                
                return {
                    "package_manager": "pip",
                    "vulnerabilities": vulnerabilities,
                    "scanner": "safety"
                }
        except Exception as e:
            log(f"safety failed: {e}")
    
    return {
        "package_manager": "pip",
        "vulnerabilities": [],
        "error": "No vulnerability scanner available (pip-audit or safety required)"
    }


def scan_all_vulnerabilities(component_dir: str) -> Dict[str, Any]:
    """Scan all package managers for vulnerabilities."""
    results = {}
    
    comp_path = Path(component_dir)
    
    # npm
    if (comp_path / "package.json").exists():
        results["npm"] = scan_npm_vulnerabilities(component_dir)
    
    # pip
    if (comp_path / "requirements.txt").exists() or (comp_path / "setup.py").exists():
        results["pip"] = scan_pip_vulnerabilities(component_dir)
    
    return results


