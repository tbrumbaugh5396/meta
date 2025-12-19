"""Unit tests for package manager utilities."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from meta.utils.packages import (
    detect_package_managers,
    install_npm_dependencies,
    install_pip_dependencies,
    install_component_dependencies
)


class TestPackageManagerDetection:
    """Tests for package manager detection."""
    
    def test_detect_npm(self):
        """Test detecting npm package manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            comp_dir = Path(tmpdir)
            (comp_dir / "package.json").write_text('{"name": "test"}')
            
            detected = detect_package_managers(str(comp_dir))
            
            assert "npm" in detected
    
    def test_detect_pip_requirements_txt(self):
        """Test detecting pip from requirements.txt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            comp_dir = Path(tmpdir)
            (comp_dir / "requirements.txt").write_text("requests==1.0.0")
            
            detected = detect_package_managers(str(comp_dir))
            
            assert "pip" in detected
    
    def test_detect_pip_setup_py(self):
        """Test detecting pip from setup.py."""
        with tempfile.TemporaryDirectory() as tmpdir:
            comp_dir = Path(tmpdir)
            (comp_dir / "setup.py").write_text("from setuptools import setup")
            
            detected = detect_package_managers(str(comp_dir))
            
            assert "pip" in detected
    
    def test_detect_cargo(self):
        """Test detecting cargo package manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            comp_dir = Path(tmpdir)
            (comp_dir / "Cargo.toml").write_text('[package]\nname = "test"')
            
            detected = detect_package_managers(str(comp_dir))
            
            assert "cargo" in detected
    
    def test_detect_go(self):
        """Test detecting go package manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            comp_dir = Path(tmpdir)
            (comp_dir / "go.mod").write_text("module test")
            
            detected = detect_package_managers(str(comp_dir))
            
            assert "go" in detected
    
    def test_detect_multiple(self):
        """Test detecting multiple package managers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            comp_dir = Path(tmpdir)
            (comp_dir / "package.json").write_text('{"name": "test"}')
            (comp_dir / "requirements.txt").write_text("requests==1.0.0")
            
            detected = detect_package_managers(str(comp_dir))
            
            assert "npm" in detected
            assert "pip" in detected
    
    def test_detect_none(self):
        """Test detecting no package managers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            comp_dir = Path(tmpdir)
            # Empty directory
            
            detected = detect_package_managers(str(comp_dir))
            
            assert len(detected) == 0


class TestPackageInstallation:
    """Tests for package installation."""
    
    def test_install_npm_dependencies_success(self):
        """Test successful npm installation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            comp_dir = Path(tmpdir)
            (comp_dir / "package.json").write_text('{"name": "test"}')
            
            with patch('meta.utils.packages.shutil.which', return_value="/usr/bin/npm"), \
                 patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                
                result = install_npm_dependencies(str(comp_dir))
                
                assert result is True
                mock_run.assert_called()
    
    def test_install_npm_dependencies_no_npm(self):
        """Test npm installation when npm is not available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            comp_dir = Path(tmpdir)
            
            with patch('meta.utils.packages.shutil.which', return_value=None):
                result = install_npm_dependencies(str(comp_dir))
                
                assert result is False
    
    def test_install_pip_dependencies_success(self):
        """Test successful pip installation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            comp_dir = Path(tmpdir)
            (comp_dir / "requirements.txt").write_text("requests==1.0.0")
            
            with patch('meta.utils.packages.shutil.which', return_value="/usr/bin/pip"), \
                 patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                
                result = install_pip_dependencies(str(comp_dir))
                
                assert result is True
                mock_run.assert_called()
    
    def test_install_component_dependencies_skip(self):
        """Test skipping package installation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            comp_dir = Path(tmpdir)
            
            result = install_component_dependencies(str(comp_dir), skip_packages=True)
            
            assert result is True
    
    def test_install_component_dependencies_none_detected(self):
        """Test installation when no package managers detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            comp_dir = Path(tmpdir)
            # Empty directory, no package files
            
            result = install_component_dependencies(str(comp_dir), skip_packages=False)
            
            assert result is True  # Should succeed when nothing to install


