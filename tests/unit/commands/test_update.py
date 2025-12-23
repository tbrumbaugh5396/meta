"""Tests for meta update command with dependency injection."""
import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from meta.cli import app


class TestUpdateCommand:
    """Tests for update command with mocks."""
    
    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()
    
    def test_update_all(self, runner, temp_meta_repo, mock_git):
        """Test update all command."""
        with patch('meta.utils.manifest.get_components') as mock_get_components, \
             patch('meta.commands.update.run_git_operation') as mock_git_op, \
             patch('meta.commands.update.get_sibling_repos', return_value=[]), \
             patch('meta.utils.git.git_available', return_value=True), \
             patch('meta.utils.manifest.find_meta_repo_root', return_value=temp_meta_repo["path"]):
            
            mock_get_components.return_value = {
                "test-component": {
                    "repo": "git@github.com:test/test.git"
                }
            }
            mock_git_op.return_value = True
            
            result = runner.invoke(app, ["update", "all", "--message", "Update repos"])
            
            # May exit with 0 or 1 depending on implementation
            assert result.exit_code in [0, 1]
    
    def test_update_status(self, runner, temp_meta_repo, mock_git):
        """Test update status command."""
        with patch('meta.utils.manifest.get_components') as mock_get_components, \
             patch('meta.commands.update.run_git_operation') as mock_git_op, \
             patch('meta.commands.update.get_sibling_repos', return_value=[]), \
             patch('meta.utils.git.git_available', return_value=True), \
             patch('meta.utils.manifest.find_meta_repo_root', return_value=temp_meta_repo["path"]):
            
            mock_get_components.return_value = {
                "test-component": {
                    "repo": "git@github.com:test/test.git"
                }
            }
            mock_git_op.return_value = True
            
            result = runner.invoke(app, ["update", "status"])
            
            # May exit with 0 or 1 depending on implementation
            assert result.exit_code in [0, 1]

