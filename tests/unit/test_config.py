"""Unit tests for configuration management."""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch
from meta.utils.config import Config, get_config


class TestConfig:
    """Tests for configuration management."""
    
    def test_config_init(self):
        """Test config initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(project_dir=tmpdir)
            assert config.project_dir == Path(tmpdir)
    
    def test_config_get_default(self):
        """Test getting default config value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(project_dir=tmpdir)
            value = config.get("nonexistent_key", "default_value")
            assert value == "default_value"
    
    def test_config_set_and_get(self):
        """Test setting and getting config values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(project_dir=tmpdir)
            
            # Set value
            assert config.set("test_key", "test_value") is True
            
            # Get value
            value = config.get("test_key")
            assert value == "test_value"
    
    def test_config_init_file(self):
        """Test initializing config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(project_dir=tmpdir)
            
            assert config.init_config() is True
            
            # Check file exists
            config_file = Path(tmpdir) / ".meta" / "config.yaml"
            assert config_file.exists()
            
            # Check content
            with open(config_file) as f:
                data = yaml.safe_load(f)
                assert "default_env" in data
                assert data["default_env"] == "dev"
    
    def test_get_config(self):
        """Test get_config function."""
        config = get_config()
        assert isinstance(config, Config)


