"""Unit tests for semantic version parsing and comparison."""

import pytest
from meta.utils.semver import (
    parse_version,
    compare_versions,
    satisfies_range,
    VersionComparison,
    find_compatible_versions
)


class TestSemanticVersion:
    """Tests for semantic version utilities."""
    
    def test_parse_version(self):
        """Test parsing semantic versions."""
        parsed = parse_version("1.2.3")
        assert parsed == (1, 2, 3, None)
        
        parsed = parse_version("v1.2.3")
        assert parsed == (1, 2, 3, None)
        
        parsed = parse_version("1.2.3-alpha")
        assert parsed == (1, 2, 3, "alpha")
    
    def test_compare_versions(self):
        """Test comparing versions."""
        assert compare_versions("1.0.0", "2.0.0") == VersionComparison.LESS
        assert compare_versions("2.0.0", "1.0.0") == VersionComparison.GREATER
        assert compare_versions("1.0.0", "1.0.0") == VersionComparison.EQUAL
        
        assert compare_versions("1.0.0", "1.0.1") == VersionComparison.LESS
        assert compare_versions("1.1.0", "1.0.0") == VersionComparison.GREATER
    
    def test_satisfies_range_exact(self):
        """Test exact version matching."""
        assert satisfies_range("1.0.0", "1.0.0") is True
        assert satisfies_range("1.0.0", "2.0.0") is False
    
    def test_satisfies_range_greater_equal(self):
        """Test >= range matching."""
        assert satisfies_range("1.0.0", ">=1.0.0") is True
        assert satisfies_range("2.0.0", ">=1.0.0") is True
        assert satisfies_range("0.9.0", ">=1.0.0") is False
    
    def test_satisfies_range_caret(self):
        """Test ^ range matching."""
        assert satisfies_range("1.2.3", "^1.0.0") is True
        assert satisfies_range("2.0.0", "^1.0.0") is False
        assert satisfies_range("1.9.9", "^1.0.0") is True
    
    def test_find_compatible_versions(self):
        """Test finding compatible versions."""
        available = ["1.0.0", "1.1.0", "2.0.0", "2.1.0"]
        compatible = find_compatible_versions("^1.0.0", available)
        
        assert "1.0.0" in compatible
        assert "1.1.0" in compatible
        assert "2.0.0" not in compatible


