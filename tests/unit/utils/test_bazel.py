"""Tests for Bazel utilities with dependency injection."""
import pytest
from unittest.mock import patch, MagicMock


class TestBazelUtils:
    """Tests for Bazel utility functions."""
    
    def test_bazel_available(self):
        """Test Bazel availability check."""
        from meta.utils.bazel import bazel_available
        import shutil
        
        # Test when bazel is available
        with patch('shutil.which', return_value="/usr/bin/bazel"):
            assert bazel_available() is True
        
        # Test when bazel is not available
        with patch('shutil.which', return_value=None):
            assert bazel_available() is False
    
    def test_run_bazel_build(self, temp_meta_repo, mock_bazel):
        """Test running Bazel build."""
        from meta.utils.bazel import run_bazel_build
        
        with patch('meta.utils.bazel.bazel_available', return_value=True), \
             patch('subprocess.run') as mock_subprocess:
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_subprocess.return_value = mock_result
            
            result = run_bazel_build(
                str(temp_meta_repo["components"] / "test-component"),
                "//test:all"
            )
            
            assert result is True
            mock_subprocess.assert_called()
    
    def test_run_bazel_test(self, temp_meta_repo, mock_bazel):
        """Test running Bazel tests."""
        from meta.utils.bazel import run_bazel_test
        
        with patch('meta.utils.bazel.bazel_available', return_value=True), \
             patch('subprocess.run') as mock_subprocess:
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_subprocess.return_value = mock_result
            
            result = run_bazel_test(
                str(temp_meta_repo["components"] / "test-component"),
                "//test:all"
            )
            
            assert result is True
            mock_subprocess.assert_called()
    
    def test_check_bazel_target_exists(self, temp_meta_repo, mock_bazel):
        """Test checking if Bazel target exists."""
        from meta.utils.bazel import check_bazel_target_exists
        
        with patch('meta.utils.bazel.bazel_available', return_value=True), \
             patch('subprocess.run') as mock_subprocess:
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "//test:all"
            mock_subprocess.return_value = mock_result
            
            result = check_bazel_target_exists("//test:all")
            
            assert result is True
            mock_subprocess.assert_called()
    
    def test_bazel_unavailable(self, temp_meta_repo):
        """Test behavior when Bazel is not available."""
        from meta.utils.bazel import run_bazel_build
        
        with patch('meta.utils.bazel.bazel_available', return_value=False):
            result = run_bazel_build(
                str(temp_meta_repo["components"] / "test-component"),
                "//test:all"
            )
            
            # Should return False or handle gracefully
            assert result is False

