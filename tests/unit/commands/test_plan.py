"""Tests for meta plan command with dependency injection."""
import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from meta.cli import app


class TestPlanCommand:
    """Tests for plan command with mocks."""
    
    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()
    
    def test_plan_with_mocks(self, runner, temp_meta_repo, mock_git, mock_manifest):
        """Test plan command with all dependencies mocked."""
        with patch('meta.commands.plan.get_components') as mock_get_components, \
             patch('meta.commands.plan.get_environment_config') as mock_get_env, \
             patch('meta.commands.plan.get_current_version') as mock_get_current:
            
            mock_get_components.return_value = {
                "test-component": {
                    "version": "v1.0.0",
                    "type": "bazel"
                }
            }
            mock_get_env.return_value = {}
            mock_get_current.return_value = None  # Component not checked out
            
            result = runner.invoke(app, ["plan", "--env", "dev"])
            
            assert result.exit_code == 0
    
    def test_compute_changes_function(self, temp_meta_repo, mock_git):
        """Test compute_changes function directly."""
        from meta.commands.plan import compute_changes
        
        with patch('meta.commands.plan.get_components') as mock_get_components, \
             patch('meta.commands.plan.get_environment_config') as mock_get_env, \
             patch('meta.commands.plan.get_current_version') as mock_get_current, \
             patch('meta.commands.plan.compare_versions') as mock_compare:
            
            mock_get_components.return_value = {
                "test-component": {
                    "version": "v1.0.0",
                    "type": "bazel"
                }
            }
            mock_get_env.return_value = {}
            mock_get_current.return_value = None
            mock_compare.return_value = 0
            
            changes = compute_changes("dev", str(temp_meta_repo["manifests"]))
            
            assert "new" in changes
            assert "upgrades" in changes
            assert "downgrades" in changes
            assert "unchanged" in changes
    
    def test_plan_with_upgrades(self, runner, temp_meta_repo, mock_git):
        """Test plan command showing upgrades."""
        with patch('meta.commands.plan.get_components') as mock_get_components, \
             patch('meta.commands.plan.get_environment_config') as mock_get_env, \
             patch('meta.commands.plan.get_current_version') as mock_get_current, \
             patch('meta.commands.plan.compare_versions') as mock_compare:
            
            mock_get_components.return_value = {
                "test-component": {
                    "version": "v2.0.0",
                    "type": "bazel"
                }
            }
            mock_get_env.return_value = {}
            mock_get_current.return_value = "v1.0.0"
            mock_compare.return_value = -1  # Current < desired (upgrade)
            
            result = runner.invoke(app, ["plan", "--env", "dev"])
            
            assert result.exit_code == 0
    
    def test_plan_with_downgrades(self, runner, temp_meta_repo, mock_git):
        """Test plan command showing downgrades."""
        with patch('meta.commands.plan.get_components') as mock_get_components, \
             patch('meta.commands.plan.get_environment_config') as mock_get_env, \
             patch('meta.commands.plan.get_current_version') as mock_get_current, \
             patch('meta.commands.plan.compare_versions') as mock_compare:
            
            mock_get_components.return_value = {
                "test-component": {
                    "version": "v1.0.0",
                    "type": "bazel"
                }
            }
            mock_get_env.return_value = {}
            mock_get_current.return_value = "v2.0.0"
            mock_compare.return_value = 1  # Current > desired (downgrade)
            
            result = runner.invoke(app, ["plan", "--env", "dev"])
            
            assert result.exit_code == 0
    
    def test_plan_specific_component(self, runner, temp_meta_repo, mock_git):
        """Test plan command for specific component."""
        with patch('meta.commands.plan.get_components') as mock_get_components, \
             patch('meta.commands.plan.get_environment_config') as mock_get_env, \
             patch('meta.commands.plan.get_current_version') as mock_get_current:
            
            mock_get_components.return_value = {
                "test-component": {
                    "version": "v1.0.0",
                    "type": "bazel"
                }
            }
            mock_get_env.return_value = {}
            mock_get_current.return_value = None
            
            result = runner.invoke(app, ["plan", "--env", "dev", "--component", "test-component"])
            
            assert result.exit_code == 0


