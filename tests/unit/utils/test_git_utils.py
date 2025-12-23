"""Tests for git utilities with dependency injection."""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock


class TestGitUtils:
    """Tests for git utility functions."""
    
    def test_git_available(self):
        """Test git availability check."""
        from meta.utils.git import git_available
        
        with patch('shutil.which', return_value="/usr/bin/git"):
            assert git_available() is True
        
        with patch('shutil.which', return_value=None):
            assert git_available() is False
    
    def test_clone_repo(self, temp_meta_repo, mock_git):
        """Test cloning a repository."""
        from meta.utils.git import clone_repo
        
        with patch('meta.utils.git.git_available', return_value=True), \
             patch('subprocess.run') as mock_subprocess, \
             patch('meta.utils.git.checkout_version', return_value=True):
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_subprocess.return_value = mock_result
            
            result = clone_repo(
                "git@github.com:test/test.git",
                str(temp_meta_repo["components"] / "test-component"),
                "v1.0.0"
            )
            
            assert result is True
            mock_subprocess.assert_called()
    
    def test_clone_repo_already_exists(self, temp_meta_repo):
        """Test cloning when directory already exists."""
        from meta.utils.git import clone_repo
        
        comp_dir = temp_meta_repo["components"] / "test-component"
        comp_dir.mkdir()
        
        with patch('meta.utils.git.git_available', return_value=True):
            result = clone_repo(
                "git@github.com:test/test.git",
                str(comp_dir),
                "v1.0.0"
            )
            
            # Should return True if directory exists
            assert result is True
    
    def test_checkout_version(self, temp_meta_repo, mock_git):
        """Test checking out a version."""
        from meta.utils.git import checkout_version
        
        comp_dir = temp_meta_repo["components"] / "test-component"
        comp_dir.mkdir()
        
        with patch('meta.utils.git.git_available', return_value=True), \
             patch('subprocess.run') as mock_subprocess:
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_subprocess.return_value = mock_result
            
            result = checkout_version(str(comp_dir), "v1.0.0")
            
            assert result is True
            mock_subprocess.assert_called()
    
    def test_get_commit_sha_for_ref(self, temp_meta_repo, mock_git):
        """Test getting commit SHA for a reference."""
        from meta.utils.git import get_commit_sha_for_ref
        
        comp_dir = temp_meta_repo["components"] / "test-component"
        comp_dir.mkdir()
        
        with patch('meta.utils.git.git_available', return_value=True), \
             patch('subprocess.run') as mock_subprocess:
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "abc123def456\n"
            mock_subprocess.return_value = mock_result
            
            sha = get_commit_sha_for_ref(str(comp_dir), "v1.0.0")
            
            assert sha == "abc123def456"
            mock_subprocess.assert_called()
    
    def test_get_current_version(self, temp_meta_repo, mock_git):
        """Test getting current version."""
        from meta.utils.git import get_current_version
        
        comp_dir = temp_meta_repo["components"] / "test-component"
        comp_dir.mkdir()
        
        with patch('meta.utils.git.git_available', return_value=True), \
             patch('subprocess.run') as mock_subprocess:
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "v1.0.0\n"
            mock_subprocess.return_value = mock_result
            
            version = get_current_version(str(comp_dir))
            
            assert version == "v1.0.0"
    
    def test_get_current_version_not_git_repo(self, temp_meta_repo):
        """Test getting current version from non-git directory."""
        from meta.utils.git import get_current_version
        
        comp_dir = temp_meta_repo["components"] / "test-component"
        comp_dir.mkdir()
        
        with patch('meta.utils.git.git_available', return_value=True), \
             patch('subprocess.run') as mock_subprocess:
            
            mock_result = MagicMock()
            mock_result.returncode = 128  # Git error
            mock_subprocess.return_value = mock_result
            
            version = get_current_version(str(comp_dir))
            
            assert version is None
    
    def test_pull_latest(self, temp_meta_repo, mock_git):
        """Test pulling latest changes."""
        from meta.utils.git import pull_latest
        
        comp_dir = temp_meta_repo["components"] / "test-component"
        comp_dir.mkdir()
        
        with patch('meta.utils.git.git_available', return_value=True), \
             patch('subprocess.run') as mock_subprocess:
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_subprocess.return_value = mock_result
            
            result = pull_latest(str(comp_dir))
            
            assert result is True
            mock_subprocess.assert_called()


