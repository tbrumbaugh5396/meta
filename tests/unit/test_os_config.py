"""Unit tests for OS configuration utilities."""

import pytest
import tempfile
from pathlib import Path
from meta.utils.os_config import OSManifest, get_os_manifest


class TestOSManifest:
    """Tests for OSManifest."""
    
    def test_init_creates_default_config(self):
        """Test that init creates default config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "os-manifest.yaml"
            manifest = OSManifest(manifest_path)
            
            assert "os" in manifest.config
            assert "packages" in manifest.config
            assert "services" in manifest.config
    
    def test_add_package(self):
        """Test adding a package."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "os-manifest.yaml"
            manifest = OSManifest(manifest_path)
            
            manifest.add_package("nginx", "latest")
            assert len(manifest.config["packages"]) == 1
            assert manifest.config["packages"][0]["name"] == "nginx"
    
    def test_add_service(self):
        """Test adding a service."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "os-manifest.yaml"
            manifest = OSManifest(manifest_path)
            
            manifest.add_service("nginx", enabled=True)
            assert len(manifest.config["services"]) == 1
            assert manifest.config["services"][0]["name"] == "nginx"
            assert manifest.config["services"][0]["enabled"] is True
    
    def test_add_user(self):
        """Test adding a user."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "os-manifest.yaml"
            manifest = OSManifest(manifest_path)
            
            manifest.add_user("appuser", groups=["www-data"], home="/home/appuser")
            assert len(manifest.config["users"]) == 1
            assert manifest.config["users"][0]["username"] == "appuser"
    
    def test_add_file(self):
        """Test adding a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "os-manifest.yaml"
            manifest = OSManifest(manifest_path)
            
            manifest.add_file("/etc/nginx/nginx.conf", content="user www-data;", mode="0644")
            assert len(manifest.config["files"]) == 1
            assert manifest.config["files"][0]["path"] == "/etc/nginx/nginx.conf"
    
    def test_validate(self):
        """Test manifest validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = Path(tmpdir) / "os-manifest.yaml"
            manifest = OSManifest(manifest_path)
            
            # Valid manifest
            errors = manifest.validate()
            assert len(errors) == 0
            
            # Invalid manifest (missing OS name)
            manifest.config["os"] = {}
            errors = manifest.validate()
            assert len(errors) > 0


