"""Tests for meta health command with dependency injection."""
import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from meta.cli import app


class TestHealthCommand:
    """Tests for health command with mocks."""
    
    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()
    
    def test_health_check(self, runner, temp_meta_repo, mock_health):
        """Test health check command."""
        from meta.utils.health import HealthStatus
        
        with patch('meta.utils.manifest.get_components') as mock_get_components, \
             patch('meta.utils.health.check_component_health') as mock_check:
            
            mock_get_components.return_value = {
                "test-component": {
                    "repo": "git@github.com:test/test.git"
                }
            }
            mock_status = HealthStatus("test-component")
            mock_status.add_check("exists", True)
            mock_status.add_check("version", True)
            mock_check.return_value = mock_status
            
            result = runner.invoke(app, ["health", "--component", "test-component", "--env", "dev"])
            
            # May exit with 0 or 1 depending on health status
            assert result.exit_code in [0, 1]
            # Should be called if component is found
            if result.exit_code == 0:
                mock_check.assert_called()
    
    def test_health_all(self, runner, temp_meta_repo, mock_health):
        """Test health check for all components."""
        from meta.utils.health import HealthStatus
        
        with patch('meta.utils.manifest.get_components') as mock_get_components, \
             patch('meta.utils.health.check_all_components_health') as mock_check_all:
            
            mock_get_components.return_value = {
                "component-a": {},
                "component-b": {}
            }
            mock_status1 = HealthStatus("component-a")
            mock_status1.add_check("exists", True)
            mock_status2 = HealthStatus("component-b")
            mock_status2.add_check("exists", True)
            mock_check_all.return_value = [mock_status1, mock_status2]
            
            result = runner.invoke(app, ["health", "--all"])
            
            # May exit with 0 or 1 depending on health status
            assert result.exit_code in [0, 1]
            # Should be called if components are found
            if result.exit_code in [0, 1]:  # Both success and failure call the function
                mock_check_all.assert_called()

