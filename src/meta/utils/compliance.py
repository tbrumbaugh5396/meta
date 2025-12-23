"""Component compliance reporting utilities."""

import json
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error
from meta.utils.manifest import get_components
from meta.utils.health import check_component_health
from meta.utils.licenses import check_license_compliance
from meta.utils.security import scan_vulnerabilities
from meta.utils.policies import check_policies


def generate_compliance_report(
    component: Optional[str] = None,
    manifests_dir: str = "manifests"
) -> Dict[str, Any]:
    """Generate compliance report."""
    report = {
        "components": {},
        "summary": {
            "total": 0,
            "compliant": 0,
            "non_compliant": 0,
            "warnings": 0
        }
    }
    
    components = get_components(manifests_dir)
    
    if component:
        components = {component: components[component]} if component in components else {}
    
    for comp_name, comp in components.items():
        comp_report = {
            "name": comp_name,
            "compliant": True,
            "issues": [],
            "warnings": [],
            "checks": {}
        }
        
        # Health check
        health = check_component_health(comp_name, manifests_dir=manifests_dir)
        comp_report["checks"]["health"] = health.get("healthy", False)
        if not health.get("healthy"):
            comp_report["compliant"] = False
            comp_report["issues"].append("Health check failed")
        
        # License compliance
        license_check = check_license_compliance(comp_name, manifests_dir=manifests_dir)
        comp_report["checks"]["license"] = license_check.get("compliant", False)
        if not license_check.get("compliant"):
            comp_report["compliant"] = False
            comp_report["issues"].extend(license_check.get("violations", []))
        
        # Security scan
        security_check = scan_vulnerabilities(comp_name, manifests_dir=manifests_dir)
        comp_report["checks"]["security"] = security_check.get("safe", False)
        if not security_check.get("safe"):
            comp_report["compliant"] = False
            comp_report["issues"].extend(security_check.get("vulnerabilities", []))
        
        # Policy check
        policy_check = check_policies(comp_name, manifests_dir=manifests_dir)
        comp_report["checks"]["policies"] = policy_check.get("compliant", False)
        if not policy_check.get("compliant"):
            comp_report["warnings"].extend(policy_check.get("violations", []))
        
        report["components"][comp_name] = comp_report
        
        # Update summary
        report["summary"]["total"] += 1
        if comp_report["compliant"]:
            report["summary"]["compliant"] += 1
        else:
            report["summary"]["non_compliant"] += 1
        
        if comp_report["warnings"]:
            report["summary"]["warnings"] += 1
    
    return report


def export_compliance_report(
    report: Dict[str, Any],
    format: str = "json",
    output_file: Optional[str] = None
) -> bool:
    """Export compliance report."""
    from pathlib import Path
    
    if format == "json":
        content = json.dumps(report, indent=2)
    elif format == "yaml":
        import yaml
        content = yaml.dump(report, default_flow_style=False)
    else:
        error(f"Unsupported format: {format}")
        return False
    
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(content)
        success(f"Report exported to {output_file}")
    else:
        print(content)
    
    return True


