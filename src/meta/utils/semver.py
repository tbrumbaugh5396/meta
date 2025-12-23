"""Semantic version parsing and comparison."""

import re
from typing import Optional, Tuple, List
from enum import Enum


class VersionComparison(Enum):
    """Version comparison result."""
    LESS = -1
    EQUAL = 0
    GREATER = 1


def parse_version(version_str: str) -> Optional[Tuple[int, int, int, Optional[str]]]:
    """
    Parse semantic version string.
    Returns (major, minor, patch, prerelease) or None if invalid.
    """
    # Remove 'v' prefix if present
    version_str = version_str.lstrip('v')
    
    # Match semver pattern: major.minor.patch[-prerelease][+build]
    pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([\w\.-]+))?(?:\+([\w\.-]+))?$'
    match = re.match(pattern, version_str)
    
    if not match:
        return None
    
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))
    prerelease = match.group(4)
    # build = match.group(5)  # Not used for comparison
    
    return (major, minor, patch, prerelease)


def compare_versions(v1: str, v2: str) -> VersionComparison:
    """Compare two semantic versions."""
    parsed_v1 = parse_version(v1)
    parsed_v2 = parse_version(v2)
    
    if not parsed_v1 or not parsed_v2:
        # If either is invalid, can't compare
        return VersionComparison.EQUAL
    
    major1, minor1, patch1, pre1 = parsed_v1
    major2, minor2, patch2, pre2 = parsed_v2
    
    # Compare major
    if major1 < major2:
        return VersionComparison.LESS
    elif major1 > major2:
        return VersionComparison.GREATER
    
    # Compare minor
    if minor1 < minor2:
        return VersionComparison.LESS
    elif minor1 > minor2:
        return VersionComparison.GREATER
    
    # Compare patch
    if patch1 < patch2:
        return VersionComparison.LESS
    elif patch1 > patch2:
        return VersionComparison.GREATER
    
    # Compare prerelease
    if pre1 is None and pre2 is None:
        return VersionComparison.EQUAL
    elif pre1 is None:
        return VersionComparison.GREATER  # No prerelease > prerelease
    elif pre2 is None:
        return VersionComparison.LESS  # Prerelease < no prerelease
    else:
        # Both have prerelease, compare lexicographically
        if pre1 < pre2:
            return VersionComparison.LESS
        elif pre1 > pre2:
            return VersionComparison.GREATER
        else:
            return VersionComparison.EQUAL


def satisfies_range(version: str, range_str: str) -> bool:
    """
    Check if version satisfies a range.
    Supports: ^, ~, >=, <=, >, <, =, and exact versions.
    """
    version = version.lstrip('v')
    range_str = range_str.strip()
    
    # Exact match
    if version == range_str or f"v{version}" == range_str:
        return True
    
    # Remove 'v' prefix from range
    range_str = range_str.lstrip('v')
    
    # Caret range: ^1.2.3 means >=1.2.3 <2.0.0
    if range_str.startswith('^'):
        base_version = range_str[1:]
        parsed = parse_version(base_version)
        if not parsed:
            return False
        major, minor, patch, _ = parsed
        return satisfies_range(version, f">={base_version}") and satisfies_range(version, f"<{major + 1}.0.0")
    
    # Tilde range: ~1.2.3 means >=1.2.3 <1.3.0
    if range_str.startswith('~'):
        base_version = range_str[1:]
        parsed = parse_version(base_version)
        if not parsed:
            return False
        major, minor, patch, _ = parsed
        return satisfies_range(version, f">={base_version}") and satisfies_range(version, f"<{major}.{minor + 1}.0")
    
    # >= operator
    if range_str.startswith('>='):
        target = range_str[2:].strip()
        comp = compare_versions(version, target)
        return comp in [VersionComparison.EQUAL, VersionComparison.GREATER]
    
    # <= operator
    if range_str.startswith('<='):
        target = range_str[2:].strip()
        comp = compare_versions(version, target)
        return comp in [VersionComparison.EQUAL, VersionComparison.LESS]
    
    # > operator
    if range_str.startswith('>'):
        target = range_str[1:].strip()
        comp = compare_versions(version, target)
        return comp == VersionComparison.GREATER
    
    # < operator
    if range_str.startswith('<'):
        target = range_str[1:].strip()
        comp = compare_versions(version, target)
        return comp == VersionComparison.LESS
    
    # = operator or no operator (exact match)
    if range_str.startswith('='):
        target = range_str[1:].strip()
    else:
        target = range_str
    
    comp = compare_versions(version, target)
    return comp == VersionComparison.EQUAL


def find_compatible_versions(required_range: str, available_versions: List[str]) -> List[str]:
    """Find all versions from available_versions that satisfy required_range."""
    compatible = []
    for version in available_versions:
        if satisfies_range(version, required_range):
            compatible.append(version)
    return compatible


