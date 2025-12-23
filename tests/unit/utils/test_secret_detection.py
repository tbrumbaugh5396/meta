"""Tests for secret detection utilities."""

import pytest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
from meta.utils.secret_detection import (
    scan_file_for_secrets,
    scan_directory_for_secrets,
    detect_secrets_in_component,
    should_exclude_file
)


class TestSecretDetection:
    """Test secret detection utilities."""
    
    def test_scan_file_for_secrets_no_secrets(self, temp_meta_repo):
        """Test scanning file with no secrets."""
        test_file = temp_meta_repo["components"] / "test.py"
        test_file.write_text("def hello():\n    print('world')")
        
        secrets = scan_file_for_secrets(test_file)
        assert secrets == []
    
    def test_scan_file_for_secrets_finds_api_key(self, temp_meta_repo):
        """Test scanning file with API key."""
        test_file = temp_meta_repo["components"] / "config.py"
        test_file.write_text('api_key = "sk_live_1234567890abcdefghijklmnop"')
        
        secrets = scan_file_for_secrets(test_file)
        assert len(secrets) > 0
        assert any(s['type'] == 'api_key' for s in secrets)
    
    def test_scan_file_for_secrets_finds_password(self, temp_meta_repo):
        """Test scanning file with password."""
        test_file = temp_meta_repo["components"] / "config.py"
        test_file.write_text('password = "mysecretpassword123"')
        
        secrets = scan_file_for_secrets(test_file)
        assert len(secrets) > 0
        assert any(s['type'] == 'password' for s in secrets)
    
    def test_should_exclude_file_git(self):
        """Test excluding .git files."""
        file_path = Path(".git/config")
        assert should_exclude_file(file_path) is True
    
    def test_should_exclude_file_node_modules(self):
        """Test excluding node_modules."""
        file_path = Path("node_modules/package/index.js")
        assert should_exclude_file(file_path) is True
    
    def test_should_exclude_file_pyc(self):
        """Test excluding .pyc files."""
        file_path = Path("module.pyc")
        assert should_exclude_file(file_path) is True
    
    def test_should_not_exclude_normal_file(self):
        """Test not excluding normal files."""
        file_path = Path("src/main.py")
        assert should_exclude_file(file_path) is False
    
    @patch("meta.utils.secret_detection.scan_file_for_secrets")
    def test_scan_directory_for_secrets(self, mock_scan_file, temp_meta_repo):
        """Test scanning directory for secrets."""
        mock_scan_file.return_value = []
        
        comp_dir = temp_meta_repo["components"] / "test-component"
        comp_dir.mkdir()
        (comp_dir / "file1.py").write_text("code")
        (comp_dir / "file2.py").write_text("code")
        
        results = scan_directory_for_secrets(comp_dir)
        
        assert results['total_secrets'] == 0
        assert results['total_files_scanned'] >= 0
    
    def test_detect_secrets_in_component_safe(self, temp_meta_repo):
        """Test detecting secrets in safe component."""
        comp_dir = temp_meta_repo["components"] / "test-component"
        comp_dir.mkdir()
        (comp_dir / "main.py").write_text("def hello(): pass")
        
        is_safe, results = detect_secrets_in_component(comp_dir, fail_on_secrets=False)
        
        assert is_safe is True
        assert results['total_secrets'] == 0
    
    def test_detect_secrets_in_component_with_secrets(self, temp_meta_repo):
        """Test detecting secrets in component with secrets."""
        comp_dir = temp_meta_repo["components"] / "test-component"
        comp_dir.mkdir()
        (comp_dir / "config.py").write_text('api_key = "sk_live_1234567890abcdefghijklmnop"')
        
        is_safe, results = detect_secrets_in_component(comp_dir, fail_on_secrets=False)
        
        assert is_safe is False
        assert results['total_secrets'] > 0
    
    def test_detect_secrets_in_component_fail_on_secrets(self, temp_meta_repo):
        """Test failing when secrets detected."""
        comp_dir = temp_meta_repo["components"] / "test-component"
        comp_dir.mkdir()
        (comp_dir / "config.py").write_text('api_key = "sk_live_1234567890abcdefghijklmnop"')
        
        is_safe, results = detect_secrets_in_component(comp_dir, fail_on_secrets=True)
        
        assert is_safe is False
        assert results['total_secrets'] > 0

