"""Version checking and validation."""

import re
from typing import Optional, Tuple


def is_valid_version(version: str) -> bool:
    """Check if version string is valid semantic version."""
    pattern = r'^v?\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$'
    return bool(re.match(pattern, version))


def normalize_version(version: str) -> str:
    """Normalize version string (remove 'v' prefix if present)."""
    return version.lstrip('v')


def compare_versions(v1: str, v2: str) -> int:
    """Compare two version strings.
    
    Returns:
        -1 if v1 < v2
         0 if v1 == v2
         1 if v1 > v2
    """
    v1_parts = [int(x) for x in normalize_version(v1).split('-')[0].split('.')]
    v2_parts = [int(x) for x in normalize_version(v2).split('-')[0].split('.')]
    
    for i in range(max(len(v1_parts), len(v2_parts))):
        v1_val = v1_parts[i] if i < len(v1_parts) else 0
        v2_val = v2_parts[i] if i < len(v2_parts) else 0
        
        if v1_val < v2_val:
            return -1
        elif v1_val > v2_val:
            return 1
    
    return 0


def check_versions(name: str, version: str) -> bool:
    """Check if a component version is valid."""
    if not is_valid_version(version):
        from meta.utils.logger import error
        error(f"Invalid version format for {name}: {version}")
        return False
    return True


