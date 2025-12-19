"""Unit tests for health check utilities."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from meta.utils.health import (
    check_component_exists,
    check_component_version,
    check_component_builds,
    check_component_tests,
    check_component_dependencies,
    check_component_health,
    HealthStatus
)


class TestHealth:
    """Tests for health check utilities."""
    
    def test_check_component_exists(self):
        """Test checking if component exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            comp_path = Path(tmpdir) / "test-component"
            comp_path.mkdir()
            
            # Mock Path to use tmpdir
            with patch('meta.utils.health.Path') as mock_path:
                mock_path.return_value = comp_path
                exists, error = check_component_exists("test-component")
                assert exists is True
                assert error is None
    
    def test_check_component_not_exists(self):
        """Test checking non-existent component."""
        exists, error = check_component_exists("nonexistent")
        assert exists is False
        assert error is not None
    
    def test_health_status(self):
        """Test HealthStatus class."""
        status = HealthStatus("test-component")
        assert status.component == "test-component"
        assert status.healthy is True
        
        status.add_check("exists", True)
        assert status.healthy is True
        
        status.add_check("builds", False, "Build failed")
        assert status.healthy is False
        assert len(status.errors) == 1
    
    def test_check_component_health(self):
        """Test comprehensive health check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            comp_path = Path(tmpdir) / "components" / "test-component"
            comp_path.mkdir(parents=True)
            
            with patch('meta.utils.health.Path') as mock_path:
                mock_path.return_value = comp_path
                with patch('meta.utils.health.check_component_exists', return_value=(True, None)):
                    with patch('meta.utils.health.check_component_version', return_value=(True, None)):
                        with patch('meta.utils.health.check_component_dependencies', return_value=(True, None)):
                            status = check_component_health("test-component", check_build=False, check_tests=False)
                            assert isinstance(status, HealthStatus)
                            assert status.component == "test-component"


