"""License compliance checking for dependencies."""

import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from meta.utils.logger import log, error, success, warning


def check_npm_licenses(component_dir: str, allowed_licenses: Optional[List[str]] = None) -> Dict[str, Any]:
    """Check npm package licenses."""
    comp_path = Path(component_dir)
    package_json = comp_path / "package.json"
    
    if not package_json.exists():
        return {"package_manager": "npm", "licenses": [], "error": "No package.json found"}
    
    if not shutil.which("npm"):
        return {"package_manager": "npm", "licenses": [], "error": "npm not available"}
    
    log(f"Checking npm licenses for {component_dir}")
    try:
        # Use license-checker if available
        if shutil.which("license-checker"):
            result = subprocess.run(
                ["license-checker", "--json"],
                cwd=component_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                license_data = json.loads(result.stdout)
                licenses = []
                violations = []
                
                for pkg_name, pkg_data in license_data.items():
                    license_info = {
                        "package": pkg_name,
                        "licenses": pkg_data.get("licenses", ""),
                        "repository": pkg_data.get("repository", ""),
                        "url": pkg_data.get("url", "")
                    }
                    licenses.append(license_info)
                    
                    # Check against allowed licenses
                    if allowed_licenses:
                        pkg_licenses = pkg_data.get("licenses", "").split(" OR ")
                        if not any(lic in allowed_licenses for lic in pkg_licenses):
                            violations.append(license_info)
                
                return {
                    "package_manager": "npm",
                    "licenses": licenses,
                    "violations": violations,
                    "scanner": "license-checker"
                }
        
        # Fallback: parse package.json and node_modules
        with open(package_json) as f:
            pkg_data = json.load(f)
        
        licenses = []
        if "license" in pkg_data:
            licenses.append({
                "package": pkg_data.get("name", "root"),
                "licenses": pkg_data["license"],
                "type": "root"
            })
        
        return {
            "package_manager": "npm",
            "licenses": licenses,
            "violations": [],
            "scanner": "package.json"
        }
    except Exception as e:
        return {"package_manager": "npm", "licenses": [], "error": str(e)}


def check_pip_licenses(component_dir: str, allowed_licenses: Optional[List[str]] = None) -> Dict[str, Any]:
    """Check pip package licenses."""
    comp_path = Path(component_dir)
    requirements_txt = comp_path / "requirements.txt"
    
    if not requirements_txt.exists():
        return {"package_manager": "pip", "licenses": [], "error": "No requirements.txt found"}
    
    # Try pip-licenses if available
    if shutil.which("pip-licenses"):
        log(f"Checking pip licenses with pip-licenses for {component_dir}")
        try:
            result = subprocess.run(
                ["pip-licenses", "--format", "json"],
                cwd=component_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                license_data = json.loads(result.stdout)
                licenses = []
                violations = []
                
                for pkg_info in license_data:
                    license_info = {
                        "package": pkg_info.get("Name", ""),
                        "version": pkg_info.get("Version", ""),
                        "licenses": pkg_info.get("License", ""),
                        "url": pkg_info.get("URL", "")
                    }
                    licenses.append(license_info)
                    
                    # Check against allowed licenses
                    if allowed_licenses:
                        pkg_license = pkg_info.get("License", "")
                        if pkg_license not in allowed_licenses:
                            violations.append(license_info)
                
                return {
                    "package_manager": "pip",
                    "licenses": licenses,
                    "violations": violations,
                    "scanner": "pip-licenses"
                }
        except Exception as e:
            log(f"pip-licenses failed: {e}")
    
    return {
        "package_manager": "pip",
        "licenses": [],
        "error": "No license scanner available (pip-licenses required)"
    }


def check_all_licenses(component_dir: str, allowed_licenses: Optional[List[str]] = None) -> Dict[str, Any]:
    """Check all package managers for licenses."""
    results = {}
    
    comp_path = Path(component_dir)
    
    # npm
    if (comp_path / "package.json").exists():
        results["npm"] = check_npm_licenses(component_dir, allowed_licenses)
    
    # pip
    if (comp_path / "requirements.txt").exists() or (comp_path / "setup.py").exists():
        results["pip"] = check_pip_licenses(component_dir, allowed_licenses)
    
    return results


def check_license_compliance(
    component: str,
    manifests_dir: str = "manifests",
    allowed_licenses: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Check license compliance for a component."""
    from meta.utils.manifest import get_components
    
    components = get_components(manifests_dir)
    if component not in components:
        return {
            "component": component,
            "compliant": False,
            "error": f"Component {component} not found"
        }
    
    comp_info = components[component]
    comp_type = comp_info.get("type", "unknown")
    
    # Determine component directory
    comp_dir = Path(f"components/{component}")
    if not comp_dir.exists():
        return {
            "component": component,
            "compliant": False,
            "error": f"Component directory not found: {comp_dir}"
        }
    
    # Check licenses
    license_results = check_all_licenses(str(comp_dir), allowed_licenses)
    
    # Determine compliance
    compliant = True
    violations = []
    
    for pm, pm_results in license_results.items():
        if "error" in pm_results:
            continue
        if "violations" in pm_results and pm_results["violations"]:
            compliant = False
            violations.extend(pm_results["violations"])
    
    return {
        "component": component,
        "compliant": compliant,
        "package_managers": license_results,
        "violations": violations
    }


