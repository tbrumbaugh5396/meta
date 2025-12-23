"""Tests for meta validate command with dependency injection."""
import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from meta.cli import app


class TestValidateCommand:
    """Tests for validate command with mocks."""
    
    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()
    
    def test_validate_with_mocks(self, runner, temp_meta_repo, mock_manifest, mock_bazel):
        """Test validate command with all dependencies mocked."""
        with patch('meta.commands.validate.get_components') as mock_get_components, \
             patch('meta.commands.validate.get_environment_config') as mock_get_env, \
             patch('meta.commands.validate.check_versions') as mock_check_versions, \
             patch('meta.commands.validate.bazel_available') as mock_bazel_avail, \
             patch('meta.commands.validate.check_bazel_target_exists') as mock_bazel_target:
            
            mock_get_components.return_value = {
                "test-component": {
                    "repo": "git@github.com:test/test.git",
                    "version": "v1.0.0",
                    "type": "bazel",
                    "build_target": "//test:all"
                }
            }
            mock_get_env.return_value = {"test-component": "v1.0.0"}
            mock_check_versions.return_value = True
            mock_bazel_avail.return_value = True
            mock_bazel_target.return_value = True
            
            result = runner.invoke(app, ["validate", "--env", "dev"])
            
            assert result.exit_code == 0
            mock_check_versions.assert_called()
    
    def test_validate_components_function(self, temp_meta_repo, mock_manifest, mock_bazel):
        """Test validate_components function directly."""
        from meta.commands.validate import validate_components
        
        with patch('meta.commands.validate.get_components') as mock_get_components, \
             patch('meta.commands.validate.get_environment_config') as mock_get_env, \
             patch('meta.commands.validate.check_versions', return_value=True), \
             patch('meta.commands.validate.bazel_available', return_value=True), \
             patch('meta.commands.validate.check_bazel_target_exists', return_value=True):
            
            mock_get_components.return_value = {
                "test-component": {
                    "version": "v1.0.0",
                    "type": "bazel",
                    "build_target": "//test:all"
                }
            }
            mock_get_env.return_value = {}
            
            result = validate_components("dev", str(temp_meta_repo["manifests"]))
            
            assert result is True
    
    def test_validate_features(self, runner, temp_meta_repo, mock_manifest):
        """Test feature validation."""
        with patch('meta.utils.manifest.get_features') as mock_get_features, \
             patch('meta.utils.manifest.get_components') as mock_get_components, \
             patch('meta.commands.validate.validate_features') as mock_validate_features, \
             patch('meta.commands.validate.validate_components', return_value=True), \
             patch('meta.commands.validate.validate_dependencies', return_value=True):
            
            mock_get_features.return_value = {
                "test-feature": {
                    "components": ["test-component"],
                    "description": "Test feature"
                }
            }
            mock_get_components.return_value = {
                "test-component": {
                    "version": "v1.0.0",
                    "type": "bazel"
                }
            }
            mock_validate_features.return_value = True
            
            result = runner.invoke(app, ["validate", "--env", "dev"])
            
            assert result.exit_code == 0
    
    def test_validate_dependencies(self, runner, temp_meta_repo, mock_dependencies):
        """Test dependency validation."""
        with patch('meta.commands.validate.validate_dependencies') as mock_validate_deps, \
             patch('meta.commands.validate.validate_components', return_value=True), \
             patch('meta.commands.validate.validate_features', return_value=True), \
             patch('meta.utils.manifest.get_components') as mock_get_components:
            
            mock_get_components.return_value = {
                "test-component": {
                    "version": "v1.0.0",
                    "type": "bazel"
                }
            }
            mock_validate_deps.return_value = True
            
            result = runner.invoke(app, ["validate", "--env", "dev"])
            
            assert result.exit_code == 0
            mock_validate_deps.assert_called()
    
    def test_validate_with_bazel_unavailable(self, runner, temp_meta_repo):
        """Test validate when Bazel is not available."""
        with patch('meta.utils.manifest.get_components') as mock_get_components, \
             patch('meta.utils.manifest.get_environment_config') as mock_get_env, \
             patch('meta.utils.version.check_versions', return_value=True), \
             patch('meta.utils.bazel.bazel_available', return_value=False), \
             patch('meta.commands.validate.validate_features', return_value=True), \
             patch('meta.commands.validate.validate_dependencies', return_value=True):
            
            mock_get_components.return_value = {
                "test-component": {
                    "version": "v1.0.0",
                    "type": "bazel",
                    "build_target": "//test:all"
                }
            }
            mock_get_env.return_value = {}
            
            result = runner.invoke(app, ["validate", "--env", "dev", "--skip-bazel"])
            
            # Should not fail if Bazel is unavailable and --skip-bazel is used
            assert result.exit_code == 0

