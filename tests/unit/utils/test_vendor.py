"""Tests for vendor utilities."""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import yaml
from meta.utils.vendor import (
    is_vendored_mode,
    vendor_component,
    get_vendor_info,
    is_component_vendored,
    convert_to_vendored_mode,
    convert_to_reference_mode,
    convert_to_vendored_for_production
)


class TestVendorUtils:
    """Test vendor utility functions."""
    
    def test_is_vendored_mode_true(self, temp_manifests):
        """Test detecting vendored mode."""
        # Create components.yaml with vendored mode
        components_yaml = Path(temp_manifests) / "components.yaml"
        components_yaml.write_text("""
meta:
  mode: "vendored"
components: {}
""")
        
        assert is_vendored_mode(temp_manifests) is True
    
    def test_is_vendored_mode_false(self, temp_manifests):
        """Test detecting reference mode."""
        # components.yaml without mode defaults to reference
        components_yaml = Path(temp_manifests) / "components.yaml"
        components_yaml.write_text("components: {}")
        
        assert is_vendored_mode(temp_manifests) is False
    
    def test_get_vendor_info(self, temp_meta_repo):
        """Test getting vendor info."""
        comp_dir = temp_meta_repo["components"] / "test-component"
        comp_dir.mkdir()
        
        vendor_info = {
            "component": "test-component",
            "repo": "git@github.com:test/test.git",
            "version": "v1.0.0",
            "vendored_at": "2024-01-15T10:30:00Z"
        }
        
        vendor_info_path = comp_dir / ".vendor-info.yaml"
        with open(vendor_info_path, 'w') as f:
            yaml.dump(vendor_info, f)
        
        result = get_vendor_info(comp_dir)
        assert result == vendor_info
    
    def test_get_vendor_info_not_vendored(self, temp_meta_repo):
        """Test getting vendor info when not vendored."""
        comp_dir = temp_meta_repo["components"] / "test-component"
        comp_dir.mkdir()
        
        result = get_vendor_info(comp_dir)
        assert result is None
    
    def test_is_component_vendored_true(self, temp_meta_repo):
        """Test checking if component is vendored."""
        comp_dir = temp_meta_repo["components"] / "test-component"
        comp_dir.mkdir()
        
        vendor_info = {
            "component": "test-component",
            "repo": "git@github.com:test/test.git",
            "version": "v1.0.0"
        }
        
        vendor_info_path = comp_dir / ".vendor-info.yaml"
        with open(vendor_info_path, 'w') as f:
            yaml.dump(vendor_info, f)
        
        with patch("meta.utils.vendor.find_meta_repo_root", return_value=temp_meta_repo["path"]):
            result = is_component_vendored("test-component")
            assert result is True
    
    def test_is_component_vendored_false(self, temp_meta_repo):
        """Test checking if component is not vendored."""
        comp_dir = temp_meta_repo["components"] / "test-component"
        comp_dir.mkdir()
        
        with patch("meta.utils.vendor.find_meta_repo_root", return_value=temp_meta_repo["path"]):
            result = is_component_vendored("test-component")
            assert result is False
    
    @patch("meta.utils.vendor.git_available", return_value=True)
    @patch("meta.utils.vendor.find_meta_repo_root")
    @patch("meta.utils.vendor.subprocess.run")
    @patch("shutil.copytree")
    @patch("shutil.rmtree")
    @patch("tempfile.TemporaryDirectory")
    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_vendor_component(self, mock_file, mock_exists, mock_tmpdir, mock_rmtree, mock_copytree, 
                              mock_subprocess, mock_find_root, mock_git_available, temp_meta_repo):
        """Test vendoring a component."""
        mock_find_root.return_value = temp_meta_repo["path"]
        mock_subprocess.return_value = MagicMock(returncode=0)
        mock_exists.return_value = False  # Component doesn't exist yet
        
        # Mock temporary directory
        tmp_path = temp_meta_repo["path"] / "tmp"
        mock_tmpdir.return_value.__enter__.return_value = str(tmp_path)
        mock_tmpdir.return_value.__exit__.return_value = None
        
        # Ensure component directory exists
        comp_dir = temp_meta_repo["components"] / "test-component"
        comp_dir.mkdir(parents=True, exist_ok=True)
        
        comp = {
            "repo": "git@github.com:test/test.git",
            "version": "v1.0.0"
        }
        
        result = vendor_component("test-component", comp)
        
        assert result is True
    
    @patch("meta.utils.vendor.is_vendored_mode", return_value=False)
    @patch("meta.utils.vendor.find_meta_repo_root")
    @patch("meta.utils.vendor.get_components")
    @patch("meta.utils.vendor.vendor_component", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="components:\n  test-component: {}")
    def test_convert_to_vendored_mode(self, mock_file, mock_vendor,
                                      mock_get_components, mock_find_root,
                                      mock_is_vendored, temp_meta_repo):
        """Test converting to vendored mode."""
        mock_find_root.return_value = temp_meta_repo["path"]
        mock_get_components.return_value = {
            "test-component": {
                "repo": "git@github.com:test/test.git",
                "version": "v1.0.0"
            }
        }
        
        components_yaml = temp_meta_repo["manifests"] / "components.yaml"
        components_yaml.write_text("components:\n  test-component: {}")
        
        # Create component directory with .git to simulate git repo
        comp_dir = temp_meta_repo["components"] / "test-component"
        comp_dir.mkdir(parents=True, exist_ok=True)
        (comp_dir / ".git").mkdir()
        
        result = convert_to_vendored_mode(str(temp_meta_repo["manifests"]))
        
        assert result is True
    
    @patch("meta.utils.vendor.is_vendored_mode", return_value=True)
    @patch("meta.utils.vendor.git_available", return_value=True)
    @patch("meta.utils.vendor.find_meta_repo_root")
    @patch("meta.utils.vendor.get_components")
    @patch("meta.utils.vendor.get_vendor_info")
    @patch("meta.utils.vendor.clone_repo", return_value=True)
    @patch("meta.utils.vendor.checkout_version", return_value=True)
    @patch("shutil.rmtree")
    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="meta:\n  mode: vendored\ncomponents:\n  test-component: {}")
    def test_convert_to_reference_mode(self, mock_file, mock_exists, mock_rmtree,
                                      mock_checkout, mock_clone, mock_get_vendor_info,
                                      mock_get_components, mock_find_root,
                                      mock_git_available, mock_is_vendored, temp_meta_repo):
        """Test converting to reference mode."""
        mock_find_root.return_value = temp_meta_repo["path"]
        mock_get_components.return_value = {
            "test-component": {
                "repo": "git@github.com:test/test.git",
                "version": "v1.0.0"
            }
        }
        mock_get_vendor_info.return_value = {
            "repo": "git@github.com:test/test.git",
            "version": "v1.0.0"
        }
        mock_exists.return_value = True
        
        components_yaml = temp_meta_repo["manifests"] / "components.yaml"
        components_yaml.write_text("meta:\n  mode: vendored\ncomponents:\n  test-component: {}")
        
        result = convert_to_reference_mode(str(temp_meta_repo["manifests"]))
        
        assert result is True
    
    @patch("meta.utils.vendor.get_environment_config")
    @patch("meta.utils.vendor.get_components")
    @patch("meta.utils.vendor.find_meta_repo_root")
    @patch("meta.utils.vendor.vendor_component", return_value=True)
    @patch("meta.utils.environment_locks.generate_environment_lock_file", return_value=True)
    @patch("shutil.rmtree")
    @patch("builtins.open", new_callable=mock_open, read_data="components:\n  test-component: {}")
    def test_convert_to_vendored_for_production(self, mock_file, mock_rmtree,
                                                 mock_generate_lock, mock_vendor,
                                                 mock_find_root, mock_get_components,
                                                 mock_get_env_config, temp_meta_repo):
        """Test converting to vendored mode for production."""
        mock_find_root.return_value = temp_meta_repo["path"]
        mock_get_components.return_value = {
            "test-component": {
                "repo": "git@github.com:test/test.git",
                "version": "v1.0.0"
            }
        }
        mock_get_env_config.return_value = {
            "test-component": "v1.2.3"  # Production version
        }
        
        components_yaml = temp_meta_repo["manifests"] / "components.yaml"
        components_yaml.write_text("components:\n  test-component: {}")
        
        result = convert_to_vendored_for_production("prod", str(temp_meta_repo["manifests"]))
        
        assert result is True

