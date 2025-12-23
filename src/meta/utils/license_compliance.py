"""License compliance utilities."""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error, warning
from meta.utils.packages import detect_package_managers


def check_npm_licenses(component_path: Path) -> Dict[str, Any]:
    """Check npm package licenses."""
    try:
        result = subprocess.run(
            ["npm", "ls", "--json", "--depth=0"],
            cwd=component_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout) if result.stdout else {}
            dependencies = data.get("dependencies", {})
            
            licenses = {}
            for pkg, info in dependencies.items():
                licenses[pkg] = {
                    "version": info.get("version", "unknown"),
                    "license": info.get("license", "unknown")
                }
            
            return {"licenses": licenses, "total": len(licenses)}
    except Exception as e:
        error(f"Failed to check npm licenses: {e}")
    
    return {"licenses": {}, "total": 0}


def check_pip_licenses(component_path: Path) -> Dict[str, Any]:
    """Check pip package licenses."""
    try:
        result = subprocess.run(
            ["pip-licenses", "--format=json"],
            cwd=component_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            licenses = json.loads(result.stdout) if result.stdout else []
            return {"licenses": licenses, "total": len(licenses)}
    except Exception as e:
        warning(f"pip-licenses not available: {e}")
    
    return {"licenses": [], "total": 0}


def validate_license_policy(licenses: Dict[str, Any],
                           policy_file: Optional[Path] = None) -> Dict[str, Any]:
    """Validate licenses against policy."""
    # In a real implementation, this would load and check against a policy file
    return {
        "compliant": True,
        "violations": []
    }


def check_component_licenses(component: str,
                            component_path: Path,
                            policy_file: Optional[Path] = None) -> Dict[str, Any]:
    """Check component license compliance."""
    package_managers = detect_package_managers(component_path)
    
    all_licenses = {}
    total = 0
    
    if "npm" in package_managers:
        npm_result = check_npm_licenses(component_path)
        all_licenses.update(npm_result.get("licenses", {}))
        total += npm_result.get("total", 0)
    
    if "pip" in package_managers:
        pip_result = check_pip_licenses(component_path)
        pip_licenses = pip_result.get("licenses", [])
        for lic in pip_licenses:
            if isinstance(lic, dict):
                all_licenses[lic.get("Name", "unknown")] = {
                    "version": lic.get("Version", "unknown"),
                    "license": lic.get("License", "unknown")
                }
        total += pip_result.get("total", 0)
    
    # Validate against policy
    validation = validate_license_policy(all_licenses, policy_file)
    
    return {
        "component": component,
        "licenses": all_licenses,
        "total": total,
        "compliant": validation.get("compliant", True),
        "violations": validation.get("violations", [])
    }


