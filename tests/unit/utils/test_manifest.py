"""Tests for manifest utilities with dependency injection."""
import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestManifestUtils:
    """Tests for manifest utility functions."""
    
    def test_find_meta_repo_root(self, temp_meta_repo):
        """Test finding meta-repo root."""
        from meta.utils.manifest import find_meta_repo_root
        
        root = find_meta_repo_root(str(temp_meta_repo["manifests"].parent))
        
        assert root is not None
        assert (root / "manifests" / "components.yaml").exists()
    
    def test_load_yaml(self, temp_meta_repo):
        """Test loading YAML file."""
        from meta.utils.manifest import load_yaml
        
        yaml_file = temp_meta_repo["manifests"] / "components.yaml"
        data = load_yaml(str(yaml_file))
        
        assert isinstance(data, dict)
        assert "components" in data
    
    def test_load_yaml_not_found(self):
        """Test loading non-existent YAML file."""
        from meta.utils.manifest import load_yaml
        
        with pytest.raises(FileNotFoundError):
            load_yaml("nonexistent.yaml")
    
    def test_get_components(self, temp_meta_repo):
        """Test getting components from manifest."""
        from meta.utils.manifest import get_components
        
        # Write test components
        components_file = temp_meta_repo["manifests"] / "components.yaml"
        components_file.write_text("""
components:
  test-component:
    repo: "git@github.com:test/test.git"
    version: "v1.0.0"
    type: "bazel"
""")
        
        components = get_components(str(temp_meta_repo["manifests"]))
        
        assert "test-component" in components
        assert components["test-component"]["version"] == "v1.0.0"
    
    def test_get_features(self, temp_meta_repo):
        """Test getting features from manifest."""
        from meta.utils.manifest import get_features
        
        # Write test features
        features_file = temp_meta_repo["manifests"] / "features.yaml"
        features_file.write_text("""
features:
  test-feature:
    components:
      - test-component
    description: "Test feature"
""")
        
        features = get_features(str(temp_meta_repo["manifests"]))
        
        assert "test-feature" in features
        assert "test-component" in features["test-feature"]["components"]
    
    def test_get_environment_config(self, temp_meta_repo):
        """Test getting environment configuration."""
        from meta.utils.manifest import get_environment_config
        
        # Write test environments
        env_file = temp_meta_repo["manifests"] / "environments.yaml"
        env_file.write_text("""
environments:
  dev:
    test-component: "v1.0.0"
  staging:
    test-component: "v1.0.0"
""")
        
        dev_config = get_environment_config("dev", str(temp_meta_repo["manifests"]))
        
        assert "test-component" in dev_config
        assert dev_config["test-component"] == "v1.0.0"
    
    def test_load_yaml_invalid(self, temp_meta_repo):
        """Test loading invalid YAML file."""
        from meta.utils.manifest import load_yaml
        
        invalid_file = temp_meta_repo["manifests"] / "invalid.yaml"
        invalid_file.write_text("invalid: yaml: content: [")
        
        with pytest.raises(Exception):  # Should raise YAMLError
            load_yaml(str(invalid_file))


