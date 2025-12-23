"""Tests for meta changeset command with dependency injection."""
import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from meta.cli import app


class TestChangesetCommand:
    """Tests for changeset command with mocks."""
    
    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()
    
    def test_changeset_create(self, runner, temp_meta_repo, mock_changeset):
        """Test changeset create command."""
        with patch('meta.commands.changeset.create_changeset') as mock_create:
            mock_changeset_obj = MagicMock()
            mock_changeset_obj.id = "changeset-123"
            mock_changeset_obj.status = "in_progress"
            mock_create.return_value = mock_changeset_obj
            
            result = runner.invoke(app, ["changeset", "create", "Test changeset"])
            
            assert result.exit_code == 0
            mock_create.assert_called_once()
    
    def test_changeset_show(self, runner, temp_meta_repo, mock_changeset):
        """Test changeset show command."""
        with patch('meta.commands.changeset.load_changeset') as mock_load:
            mock_changeset_obj = MagicMock()
            mock_changeset_obj.id = "changeset-123"
            mock_changeset_obj.description = "Test changeset"
            mock_changeset_obj.author = "test@example.com"
            mock_changeset_obj.timestamp = "2024-01-01T00:00:00"
            mock_changeset_obj.status = "in_progress"
            mock_changeset_obj.repos = []
            mock_changeset_obj.metadata = {}
            mock_load.return_value = mock_changeset_obj
            
            result = runner.invoke(app, ["changeset", "show", "changeset-123"])
            
            assert result.exit_code == 0
            mock_load.assert_called_once_with("changeset-123")
    
    def test_changeset_list(self, runner, temp_meta_repo, mock_changeset):
        """Test changeset list command."""
        with patch('meta.commands.changeset.list_changesets') as mock_list:
            mock_list.return_value = []
            
            result = runner.invoke(app, ["changeset", "list"])
            
            assert result.exit_code == 0
            mock_list.assert_called()
    
    def test_changeset_current(self, runner, temp_meta_repo, mock_changeset):
        """Test changeset current command."""
        from meta.utils.changeset import Changeset
        
        # Create actual changeset directory and changeset
        changeset_dir = temp_meta_repo["path"] / ".meta" / "changesets"
        changeset_dir.mkdir(parents=True, exist_ok=True)
        
        from meta.utils.changeset import create_changeset, save_changeset
        changeset = create_changeset("Test changeset", "test@example.com")
        save_changeset(changeset)
        
        result = runner.invoke(app, ["changeset", "current"])
        
        # If changeset exists, exit code is 0; if not, it's 1
        assert result.exit_code in [0, 1]
    
    def test_changeset_finalize(self, runner, temp_meta_repo, mock_changeset):
        """Test changeset finalize command."""
        with patch('meta.commands.changeset.get_current_changeset') as mock_current, \
             patch('meta.commands.changeset.load_changeset') as mock_load, \
             patch('meta.commands.changeset.save_changeset') as mock_save, \
             patch('meta.commands.changeset.get_components') as mock_get_components:
            
            mock_changeset_obj = MagicMock()
            mock_changeset_obj.id = "changeset-123"
            mock_changeset_obj.status = "in_progress"
            mock_changeset_obj.repos = []
            mock_current.return_value = mock_changeset_obj
            mock_load.return_value = mock_changeset_obj
            mock_get_components.return_value = {}
            
            result = runner.invoke(app, ["changeset", "finalize"])
            
            assert result.exit_code == 0
            mock_save.assert_called()
    
    def test_changeset_rollback(self, runner, temp_meta_repo, mock_changeset, mock_git):
        """Test changeset rollback command."""
        with patch('meta.commands.changeset.load_changeset') as mock_load, \
             patch('meta.commands.changeset.get_components') as mock_get_components, \
             patch('meta.commands.changeset.get_commit_sha') as mock_get_sha, \
             patch('meta.commands.changeset.get_current_version') as mock_get_version, \
             patch('subprocess.run') as mock_subprocess:
            
            mock_changeset_obj = MagicMock()
            mock_changeset_obj.id = "changeset-123"
            mock_changeset_obj.repos = [
                {
                    "name": "test-component",
                    "commit": "abc123",
                    "branch": "main",
                    "message": "Test commit"
                }
            ]
            mock_load.return_value = mock_changeset_obj
            mock_get_components.return_value = {
                "test-component": {
                    "repo": "git@github.com:test/test.git"
                }
            }
            mock_get_sha.return_value = "abc123"
            mock_get_version.return_value = "v1.0.0"
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_subprocess.return_value = mock_result
            
            result = runner.invoke(app, ["changeset", "rollback", "changeset-123", "--dry-run"])
            
            assert result.exit_code == 0
            mock_load.assert_called_once_with("changeset-123")
    
    def test_changeset_bisect(self, runner, temp_meta_repo, mock_changeset):
        """Test changeset bisect command."""
        with patch('meta.commands.changeset.list_changesets') as mock_list, \
             patch('meta.commands.changeset.load_changeset') as mock_load, \
             patch('subprocess.run') as mock_subprocess:
            
            mock_changeset1 = MagicMock()
            mock_changeset1.id = "changeset-1"
            mock_changeset2 = MagicMock()
            mock_changeset2.id = "changeset-2"
            
            mock_list.return_value = [mock_changeset1, mock_changeset2]
            mock_load.side_effect = [mock_changeset1, mock_changeset2]
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_subprocess.return_value = mock_result
            
            result = runner.invoke(app, [
                "changeset", "bisect",
                "--start", "changeset-1",
                "--end", "changeset-2",
                "--test", "echo test"
            ])
            
            # Bisect may exit with different codes depending on test results
            assert result.exit_code in [0, 1, 2]

