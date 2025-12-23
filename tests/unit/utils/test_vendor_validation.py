"""Tests for vendor validation utilities."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from meta.utils.vendor_validation import (
    validate_prerequisites,
    validate_component_for_vendor,
    validate_conversion_readiness
)


class TestVendorValidation:
    """Test vendor validation utilities."""
    
    @patch("meta.utils.vendor_validation.git_available", return_value=True)
    @patch("meta.utils.vendor_validation.find_meta_repo_root")
    @patch("meta.utils.vendor_validation.load_yaml")
    @patch("meta.utils.vendor_validation.validate_dependencies", return_value=(True, []))
    def test_validate_prerequisites_success(self, mock_validate_deps, mock_load_yaml,
                                            mock_find_root, mock_git, temp_meta_repo):
        """Test successful prerequisite validation."""
        mock_find_root.return_value = temp_meta_repo["path"]
        mock_load_yaml.return_value = {
            "components": {
                "test-component": {
                    "repo": "git@github.com:test/test.git",
                    "version": "v1.0.0"
                }
            }
        }
        
        is_valid, errors = validate_prerequisites(str(temp_meta_repo["manifests"]))
        
        assert is_valid is True
        assert len(errors) == 0
    
    @patch("meta.utils.vendor_validation.git_available", return_value=False)
    def test_validate_prerequisites_no_git(self, mock_git, temp_meta_repo):
        """Test validation fails when Git not available."""
        is_valid, errors = validate_prerequisites(str(temp_meta_repo["manifests"]))
        
        assert is_valid is False
        assert any("Git is not available" in err for err in errors)
    
    def test_validate_component_for_vendor_success(self):
        """Test successful component validation."""
        comp_data = {
            "repo": "git@github.com:test/test.git",
            "version": "v1.0.0"
        }
        
        is_valid, errors = validate_component_for_vendor("test-component", comp_data)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_component_for_vendor_missing_repo(self):
        """Test validation fails when repo missing."""
        comp_data = {
            "version": "v1.0.0"
        }
        
        is_valid, errors = validate_component_for_vendor("test-component", comp_data)
        
        assert is_valid is False
        assert any("missing required field: repo" in err for err in errors)
    
    def test_validate_component_for_vendor_invalid_version(self):
        """Test validation fails with invalid version."""
        comp_data = {
            "repo": "git@github.com:test/test.git",
            "version": "invalid-version"
        }
        
        is_valid, errors = validate_component_for_vendor("test-component", comp_data)
        
        assert is_valid is False
        assert any("invalid version format" in err for err in errors)
    
    @patch("meta.utils.vendor_validation.validate_prerequisites", return_value=(True, []))
    @patch("meta.utils.vendor_validation.validate_component_for_vendor", return_value=(True, []))
    @patch("meta.utils.vendor_validation.validate_dependencies", return_value=(True, []))
    @patch("meta.utils.vendor_validation.get_dependency_order", return_value=["test-component"])
    @patch("meta.utils.vendor_validation.is_vendored_mode", return_value=False)
    @patch("meta.utils.vendor_validation.get_components")
    @patch("meta.utils.vendor_validation.find_meta_repo_root")
    @patch("meta.utils.secret_detection.scan_directory_for_secrets")
    def test_validate_conversion_readiness_success(self, mock_scan_secrets, mock_find_root,
                                                   mock_get_components, mock_is_vendored,
                                                   mock_dep_order, mock_validate_deps,
                                                   mock_validate_comp, mock_validate_prereq,
                                                   temp_meta_repo):
        """Test successful conversion readiness validation."""
        mock_find_root.return_value = temp_meta_repo["path"]
        mock_get_components.return_value = {
            "test-component": {
                "repo": "git@github.com:test/test.git",
                "version": "v1.0.0"
            }
        }
        mock_scan_secrets.return_value = {
            'secrets_found': [],
            'total_files_scanned': 10,
            'total_secrets': 0
        }
        
        is_valid, errors, details = validate_conversion_readiness(
            "vendored",
            str(temp_meta_repo["manifests"]),
            check_secrets=True
        )
        
        assert is_valid is True
        assert len(errors) == 0
        assert details['prerequisites']['valid'] is True

