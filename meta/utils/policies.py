"""Policy enforcement utilities."""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, error
from meta.utils.manifest import get_components


POLICIES_FILE = ".meta/policies.yaml"


class PolicyEngine:
    """Policy enforcement engine."""
    
    def __init__(self, policies_file: str = POLICIES_FILE):
        self.policies_file = Path(policies_file)
        self.policies: Dict[str, Any] = self._load_policies()
    
    def _load_policies(self) -> Dict[str, Any]:
        """Load policies from file."""
        if not self.policies_file.exists():
            return {}
        
        try:
            with open(self.policies_file) as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            error(f"Failed to load policies: {e}")
            return {}
    
    def check_version_policy(self, component: str, version: str) -> tuple[bool, Optional[str]]:
        """Check if version is allowed by policy."""
        version_policies = self.policies.get("versions", {})
        
        # Check component-specific policy
        if component in version_policies:
            allowed = version_policies[component].get("allowed", [])
            if allowed and version not in allowed:
                return False, f"Version {version} not allowed for {component}"
        
        # Check global policy
        global_policy = version_policies.get("_global", {})
        min_version = global_policy.get("min_version")
        max_version = global_policy.get("max_version")
        
        if min_version and self._compare_versions(version, min_version) < 0:
            return False, f"Version {version} below minimum {min_version}"
        
        if max_version and self._compare_versions(version, max_version) > 0:
            return False, f"Version {version} above maximum {max_version}"
        
        return True, None
    
    def check_dependency_policy(self, component: str, dependencies: List[str]):
        """Check if dependencies are allowed."""
        dep_policies = self.policies.get("dependencies", {})
        
        # Check component-specific policy
        if component in dep_policies:
            allowed = dep_policies[component].get("allowed", [])
            forbidden = dep_policies[component].get("forbidden", [])
            
            for dep in dependencies:
                if allowed and dep not in allowed:
                    return False, f"Dependency {dep} not allowed for {component}"
                if dep in forbidden:
                    return False, f"Dependency {dep} forbidden for {component}"
        
        return True, None
    
    def check_security_policy(self, component: str):
        """Check if component passes security policy."""
        security_policies = self.policies.get("security", {})
        
        # Check if security scan required
        require_scan = security_policies.get("require_scan", False)
        if require_scan:
            # In a real implementation, check if scan was performed
            pass
        
        return True, None
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare two version strings."""
        from meta.utils.version import compare_versions
        return compare_versions(v1, v2)
    
    def validate_apply(self, component: str, version: str,
                      dependencies: List[str]):
        """Validate if component can be applied."""
        errors = []
        
        # Check version policy
        version_ok, version_error = self.check_version_policy(component, version)
        if not version_ok:
            errors.append(version_error)
        
        # Check dependency policy
        dep_ok, dep_error = self.check_dependency_policy(component, dependencies)
        if not dep_ok:
            errors.append(dep_error)
        
        # Check security policy
        sec_ok, sec_error = self.check_security_policy(component)
        if not sec_ok:
            errors.append(sec_error)
        
        return len(errors) == 0, errors


def get_policy_engine() -> PolicyEngine:
    """Get policy engine instance."""
    return PolicyEngine()

