"""Unit tests for lock file utilities."""

import pytest
import yaml
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from meta.utils.lock import (
    generate_lock_file,
    load_lock_file,
    get_locked_components,
    validate_lock_file
)
from meta.utils.git import get_commit_sha_for_ref


class TestLockFileGeneration:
    """Tests for lock file generation."""
    
    def test_generate_lock_file_creates_file(self):
        """Test that generate_lock_file creates a lock file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifests_dir = Path(tmpdir) / "manifests"
            manifests_dir.mkdir()
            lock_file = manifests_dir / "components.lock.yaml"
            
            # Create a minimal components.yaml
            components_yaml = manifests_dir / "components.yaml"
            components_yaml.write_text("""
components:
  test-component:
    repo: "git@github.com:test/test.git"
    version: "v1.0.0"
    type: "bazel"
""")
            
            with patch('meta.utils.lock.get_components') as mock_get_components, \
                 patch('meta.utils.lock.get_commit_sha_for_ref') as mock_get_sha, \
                 patch('meta.utils.lock.git_available', return_value=True):
                mock_get_components.return_value = {
                    "test-component": {
                        "repo": "git@github.com:test/test.git",
                        "version": "v1.0.0",
                        "type": "bazel"
                    }
                }
                mock_get_sha.return_value = "abc123def456"
                
                result = generate_lock_file(str(manifests_dir), str(lock_file))
                
                assert result is True
                assert lock_file.exists()
                
                # Verify lock file content
                with open(lock_file) as f:
                    data = yaml.safe_load(f)
                    assert "components" in data
                    assert "test-component" in data["components"]
                    assert data["components"]["test-component"]["commit"] == "abc123def456"
    
    def test_generate_lock_file_handles_missing_repo(self):
        """Test that generate_lock_file handles components without repo URLs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifests_dir = Path(tmpdir) / "manifests"
            manifests_dir.mkdir()
            lock_file = manifests_dir / "components.lock.yaml"
            
            with patch('meta.utils.lock.get_components') as mock_get_components, \
                 patch('meta.utils.lock.git_available', return_value=True):
                mock_get_components.return_value = {
                    "test-component": {
                        "version": "v1.0.0",
                        "type": "bazel"
                        # No repo URL
                    }
                }
                
                result = generate_lock_file(str(manifests_dir), str(lock_file))
                
                # Should still succeed but skip component without repo
                assert result is True
    
    def test_load_lock_file(self):
        """Test loading a lock file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_file = Path(tmpdir) / "test.lock.yaml"
            lock_file.write_text("""
generated_at: "2024-01-01T00:00:00Z"
components:
  test-component:
    version: "v1.0.0"
    commit: "abc123"
""")
            
            data = load_lock_file(str(lock_file))
            
            assert data is not None
            assert "components" in data
            assert "test-component" in data["components"]
    
    def test_load_lock_file_nonexistent(self):
        """Test loading a non-existent lock file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_file = Path(tmpdir) / "nonexistent.lock.yaml"
            
            data = load_lock_file(str(lock_file))
            
            assert data is None
    
    def test_get_locked_components(self):
        """Test getting locked components from lock file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_file = Path(tmpdir) / "test.lock.yaml"
            lock_file.write_text("""
generated_at: "2024-01-01T00:00:00Z"
components:
  test-component:
    version: "v1.0.0"
    commit: "abc123"
""")
            
            components = get_locked_components(str(lock_file))
            
            assert "test-component" in components
            assert components["test-component"]["version"] == "v1.0.0"
            assert components["test-component"]["commit"] == "abc123"
    
    def test_validate_lock_file_matches_manifest(self):
        """Test that validate_lock_file correctly validates against manifest."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifests_dir = Path(tmpdir) / "manifests"
            manifests_dir.mkdir()
            lock_file = manifests_dir / "components.lock.yaml"
            
            # Create components.yaml
            components_yaml = manifests_dir / "components.yaml"
            components_yaml.write_text("""
components:
  test-component:
    repo: "git@github.com:test/test.git"
    version: "v1.0.0"
    type: "bazel"
""")
            
            # Create matching lock file
            lock_file.write_text("""
generated_at: "2024-01-01T00:00:00Z"
components:
  test-component:
    version: "v1.0.0"
    commit: "abc123"
""")
            
            result = validate_lock_file(str(manifests_dir), str(lock_file))
            
            assert result is True
    
    def test_validate_lock_file_mismatch(self):
        """Test that validate_lock_file detects mismatches."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifests_dir = Path(tmpdir) / "manifests"
            manifests_dir.mkdir()
            lock_file = manifests_dir / "components.lock.yaml"
            
            # Create components.yaml
            components_yaml = manifests_dir / "components.yaml"
            components_yaml.write_text("""
components:
  test-component:
    repo: "git@github.com:test/test.git"
    version: "v2.0.0"  # Different version
    type: "bazel"
""")
            
            # Create lock file with different version
            lock_file.write_text("""
generated_at: "2024-01-01T00:00:00Z"
components:
  test-component:
    version: "v1.0.0"  # Mismatch
    commit: "abc123"
""")
            
            result = validate_lock_file(str(manifests_dir), str(lock_file))
            
            assert result is False


