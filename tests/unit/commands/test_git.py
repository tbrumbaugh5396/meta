"""Tests for meta git command with dependency injection."""
import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from meta.cli import app
from pathlib import Path


class TestGitCommand:
    """Tests for git command with mocks."""
    
    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()
    
    def test_git_status_all(self, runner, temp_meta_repo, mock_git):
        """Test git status --all command."""
        with patch('meta.commands.git.get_components') as mock_get_components, \
             patch('meta.commands.git.run_git_command') as mock_run_git, \
             patch('meta.commands.git.git_available', return_value=True):
            
            mock_get_components.return_value = {
                "test-component": {
                    "repo": "git@github.com:test/test.git",
                    "version": "v1.0.0"
                }
            }
            mock_run_git.return_value = (True, "On branch main", "")
            
            result = runner.invoke(app, ["git", "status", "--all"])
            
            assert result.exit_code == 0
            mock_run_git.assert_called()
    
    def test_git_commit_with_changeset(self, runner, temp_meta_repo, mock_git, mock_changeset):
        """Test git commit with changeset ID."""
        with patch('meta.utils.manifest.get_components') as mock_get_components, \
             patch('meta.commands.git.run_git_command') as mock_run_git, \
             patch('meta.utils.changeset.load_changeset') as mock_load_changeset, \
             patch('meta.utils.changeset.extract_changeset_id_from_message') as mock_extract, \
             patch('meta.utils.changeset.get_current_changeset', return_value=None), \
             patch('meta.utils.git.git_available', return_value=True), \
             patch('meta.utils.git.get_commit_sha', return_value="abc123"), \
             patch('meta.utils.git.get_current_version', return_value="v1.0.0"), \
             patch('meta.utils.manifest.find_meta_repo_root', return_value=temp_meta_repo["path"]), \
             patch('pathlib.Path.exists', return_value=True):
            
            mock_get_components.return_value = {
                "test-component": {
                    "repo": "git@github.com:test/test.git",
                    "version": "v1.0.0"
                }
            }
            mock_run_git.return_value = (True, "Commit successful", "")
            mock_extract.return_value = "changeset-123"
            
            mock_changeset_obj = MagicMock()
            mock_changeset_obj.id = "changeset-123"
            mock_load_changeset.return_value = mock_changeset_obj
            
            result = runner.invoke(app, [
                "git", "commit", "-m", "Test commit", 
                "--changeset", "changeset-123",
                "--component", "test-component"
            ])
            
            assert result.exit_code == 0
            mock_run_git.assert_called()
    
    def test_git_push_all(self, runner, temp_meta_repo, mock_git):
        """Test git push --all command."""
        with patch('meta.commands.git.get_components') as mock_get_components, \
             patch('meta.commands.git.run_git_command') as mock_run_git, \
             patch('meta.commands.git.git_available', return_value=True):
            
            mock_get_components.return_value = {
                "test-component": {
                    "repo": "git@github.com:test/test.git",
                    "version": "v1.0.0"
                }
            }
            mock_run_git.return_value = (True, "Push successful", "")
            
            result = runner.invoke(app, ["git", "push", "--all"])
            
            assert result.exit_code == 0
            mock_run_git.assert_called()
    
    def test_git_checkout_component(self, runner, temp_meta_repo, mock_git):
        """Test git checkout for specific component."""
        with patch('meta.commands.git.get_components') as mock_get_components, \
             patch('meta.commands.git.run_git_command') as mock_run_git, \
             patch('meta.commands.git.git_available', return_value=True):
            
            mock_get_components.return_value = {
                "test-component": {
                    "repo": "git@github.com:test/test.git",
                    "version": "v1.0.0"
                }
            }
            mock_run_git.return_value = (True, "Checked out v1.0.0", "")
            
            result = runner.invoke(app, [
                "git", "checkout", "v1.0.0",
                "--component", "test-component"
            ])
            
            assert result.exit_code == 0
            mock_run_git.assert_called()
    
    def test_git_log_meta_repo(self, runner, temp_meta_repo, mock_git):
        """Test git log for meta-repo."""
        with patch('meta.commands.git.run_git_command') as mock_run_git, \
             patch('meta.commands.git.git_available', return_value=True):
            
            mock_run_git.return_value = (True, "commit abc123\ncommit def456", "")
            
            result = runner.invoke(app, ["git", "log", "--oneline", "-n", "10", "--meta-repo"])
            
            assert result.exit_code == 0
            mock_run_git.assert_called()
    
    def test_run_git_command_function(self, temp_meta_repo, mock_git):
        """Test run_git_command function directly."""
        from meta.commands.git import run_git_command
        
        with patch('meta.commands.git.git_available', return_value=True), \
             patch('subprocess.run') as mock_subprocess:
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Success"
            mock_result.stderr = ""
            mock_subprocess.return_value = mock_result
            
            success, stdout, stderr = run_git_command(["status"])
            
            assert success is True
            assert stdout == "Success"
    
    def test_git_unavailable(self, runner, temp_meta_repo):
        """Test git command when git is not available."""
        with patch('meta.commands.git.git_available', return_value=False):
            
            result = runner.invoke(app, ["git", "status"])
            
            # Should handle gracefully
            assert result.exit_code != 0 or "not available" in result.output.lower()

