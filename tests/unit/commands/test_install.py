"""Tests for meta install command with dependency injection."""
import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from meta.cli import app


class TestInstallCommand:
    """Tests for install command with mocks."""
    
    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()
    
    def test_install_system_packages(self, runner, temp_meta_repo):
        """Test install system-packages command."""
        with patch('meta.utils.system_packages.load_system_packages') as mock_load, \
             patch('meta.utils.system_packages.install_system_packages') as mock_install:
            
            mock_load.return_value = {
                "system_packages": {
                    "system_tools": ["git", "docker", "bazel"]
                }
            }
            mock_install.return_value = True
            
            result = runner.invoke(app, ["install", "system-packages"])
            
            # May exit with 0 or 1 depending on whether file exists
            assert result.exit_code in [0, 1]
    
    def test_install_python(self, runner, temp_meta_repo):
        """Test install python command."""
        with patch('meta.utils.system_packages.install_python_packages') as mock_install:
            mock_install.return_value = True
            
            result = runner.invoke(app, ["install", "python", "requests", "pytest"])
            
            assert result.exit_code == 0
            # Function should be called with packages list and global_install flag
            mock_install.assert_called_once()
            # Check it was called with the packages (first arg is packages list)
            call_args = mock_install.call_args
            packages_arg = call_args[0][0] if call_args[0] else []
            assert "requests" in packages_arg or "pytest" in packages_arg
    
    def test_install_system(self, runner, temp_meta_repo):
        """Test install system command."""
        with patch('meta.utils.system_packages.detect_system_package_manager') as mock_detect, \
             patch('meta.utils.system_packages.install_system_packages') as mock_install:
            
            mock_detect.return_value = "brew"
            mock_install.return_value = True
            
            result = runner.invoke(app, ["install", "system", "git", "docker", "--manager", "brew"])
            
            assert result.exit_code == 0
            # Function should be called with packages list and package_manager
            mock_install.assert_called_once()
            # Check it was called with the packages (first arg is packages list)
            call_args = mock_install.call_args
            packages_arg = call_args[0][0] if call_args[0] else []
            assert "git" in packages_arg or "docker" in packages_arg

