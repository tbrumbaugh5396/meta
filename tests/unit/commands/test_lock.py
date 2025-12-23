"""Tests for meta lock command with dependency injection."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from meta.cli import app


class TestLockCommand:
    """Tests for lock command with mocks."""
    
    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()
    
    def test_lock_generate(self, runner, temp_meta_repo, mock_lock, mock_git):
        """Test lock file generation."""
        with patch('meta.utils.manifest.get_components') as mock_get_components, \
             patch('meta.utils.manifest.get_environment_config', return_value={}), \
             patch('meta.utils.lock.generate_lock_file') as mock_generate, \
             patch('meta.utils.environment_locks.generate_environment_lock_file') as mock_generate_env, \
             patch('meta.utils.environment_locks.get_environment_lock_file_path', return_value=Path("manifests/dev.lock.yaml")), \
             patch('meta.utils.git.get_commit_sha_for_ref') as mock_get_sha, \
             patch('meta.utils.git.git_available', return_value=True), \
             patch('pathlib.Path.exists', return_value=False), \
             patch('pathlib.Path.write_text'):
            
            mock_get_components.return_value = {
                "test-component": {
                    "repo": "git@github.com:test/test.git",
                    "version": "v1.0.0",
                    "type": "bazel"
                }
            }
            mock_get_sha.return_value = "abc123def456"
            mock_generate.return_value = True
            mock_generate_env.return_value = True
            
            result = runner.invoke(app, ["lock", "--env", "dev"])
            
            # Should succeed and call generate_environment_lock_file
            assert result.exit_code == 0
            mock_generate_env.assert_called_once()
    
    def test_lock_validate(self, runner, temp_meta_repo, mock_lock):
        """Test lock file validation."""
        with patch('meta.utils.lock.validate_lock_file') as mock_validate, \
             patch('meta.utils.environment_locks.validate_environment_lock_file') as mock_validate_env, \
             patch('meta.utils.lock.load_lock_file') as mock_load:
            
            mock_load.return_value = {
                "components": {
                    "test-component": {
                        "sha": "abc123def456",
                        "version": "v1.0.0"
                    }
                }
            }
            mock_validate.return_value = True
            mock_validate_env.return_value = True
            
            with patch('meta.utils.environment_locks.get_environment_lock_file_path', return_value=Path("manifests/dev.lock.yaml")), \
                 patch('pathlib.Path.exists', return_value=True):
                result = runner.invoke(app, ["lock", "validate", "--env", "dev"])
                
                assert result.exit_code == 0
                mock_validate_env.assert_called()
    
    def test_lock_promote(self, runner, temp_meta_repo, mock_lock):
        """Test lock file promotion between environments."""
        with patch('meta.utils.environment_locks.promote_lock_file') as mock_promote, \
             patch('meta.utils.environment_locks.get_environment_lock_file_path') as mock_get_path, \
             patch('pathlib.Path.exists', return_value=True):
            
            mock_get_path.side_effect = [
                Path("manifests/dev.lock.yaml"),
                Path("manifests/staging.lock.yaml")
            ]
            mock_promote.return_value = True
            
            result = runner.invoke(app, ["lock", "promote", "dev", "staging"])
            
            assert result.exit_code == 0
            mock_promote.assert_called_once()
    
    def test_lock_compare(self, runner, temp_meta_repo, mock_lock):
        """Test lock file comparison."""
        with patch('meta.utils.environment_locks.compare_lock_files') as mock_compare:
            mock_compare.return_value = {
                "added": [],
                "removed": [],
                "changed": []
            }
            
            with patch('meta.utils.environment_locks.get_environment_lock_file_path') as mock_get_path:
                mock_get_path.side_effect = [
                    Path("manifests/dev.lock.yaml"),
                    Path("manifests/staging.lock.yaml")
                ]
                with patch('pathlib.Path.exists', return_value=True):
                    result = runner.invoke(app, ["lock", "compare", "dev", "staging"])
                    
                    assert result.exit_code == 0
                    mock_compare.assert_called()
    
    def test_lock_with_changeset(self, runner, temp_meta_repo, mock_lock, mock_changeset):
        """Test lock generation with changeset ID."""
        with              patch('meta.utils.manifest.get_components') as mock_get_components, \
             patch('meta.utils.manifest.get_environment_config', return_value={}), \
             patch('meta.utils.manifest.get_environments', return_value={"dev": {}}), \
             patch('meta.utils.environment_locks.generate_environment_lock_file') as mock_generate_env, \
             patch('meta.utils.environment_locks.get_environment_lock_file_path', return_value=Path("manifests/dev.lock.yaml")), \
             patch('meta.utils.git.get_commit_sha_for_ref') as mock_get_sha, \
             patch('meta.utils.git.git_available', return_value=True), \
             patch('meta.utils.changeset.load_changeset') as mock_load_changeset, \
             patch('meta.utils.changeset.save_changeset'), \
             patch('meta.utils.manifest.find_meta_repo_root', return_value=temp_meta_repo["path"]), \
             patch('meta.utils.git.get_commit_sha', return_value="abc123"), \
             patch('pathlib.Path.exists', new=lambda self: True if "environments.yaml" in str(self) else False), \
             patch('pathlib.Path.write_text'), \
             patch('pathlib.Path.mkdir'), \
             patch('subprocess.run') as mock_subprocess:
            
            mock_get_components.return_value = {
                "test-component": {
                    "repo": "git@github.com:test/test.git",
                    "version": "v1.0.0"
                }
            }
            mock_get_sha.return_value = "abc123def456"
            mock_generate_env.return_value = True
            
            mock_changeset_obj = MagicMock()
            mock_changeset_obj.id = "changeset-123"
            mock_changeset_obj.add_repo_commit = MagicMock()
            mock_load_changeset.return_value = mock_changeset_obj
            
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stdout = "main"
            
            result = runner.invoke(app, ["lock", "--env", "dev", "--changeset", "changeset-123"])
            
            # Should succeed and call generate_environment_lock_file
            assert result.exit_code == 0
            mock_generate_env.assert_called_once()

