"""Unit tests for environment-specific lock files."""

import pytest
import yaml
import tempfile
from pathlib import Path
from unittest.mock import patch
from meta.utils.environment_locks import (
    generate_environment_lock_file,
    load_environment_lock_file,
    validate_environment_lock_file,
    promote_lock_file,
    compare_lock_files,
    get_environment_lock_file_path
)


class TestEnvironmentLocks:
    """Tests for environment lock files."""
    
    def test_get_environment_lock_file_path(self):
        """Test getting environment lock file path."""
        path = get_environment_lock_file_path("dev", "manifests")
        assert path == "manifests/components.lock.dev.yaml"
    
    def test_generate_environment_lock_file(self):
        """Test generating environment-specific lock file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifests_dir = Path(tmpdir) / "manifests"
            manifests_dir.mkdir()
            
            # Create components.yaml
            components_yaml = manifests_dir / "components.yaml"
            components_yaml.write_text("""
components:
  test-component:
    repo: "git@github.com:test/test.git"
    version: "v1.0.0"
    type: "bazel"
""")
            
            # Create environments.yaml
            env_yaml = manifests_dir / "environments.yaml"
            env_yaml.write_text("""
environments:
  dev:
    test-component: "dev"
""")
            
            with patch('meta.utils.environment_locks.get_commit_sha_for_ref', return_value="abc123"), \
                 patch('meta.utils.environment_locks.git_available', return_value=True):
                result = generate_environment_lock_file("dev", str(manifests_dir))
                
                assert result is True
                lock_file = manifests_dir / "components.lock.dev.yaml"
                assert lock_file.exists()
    
    def test_promote_lock_file(self):
        """Test promoting lock file between environments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifests_dir = Path(tmpdir) / "manifests"
            manifests_dir.mkdir()
            
            # Create source lock file
            source_lock = manifests_dir / "components.lock.dev.yaml"
            source_lock.write_text("""
generated_at: "2024-01-01T00:00:00Z"
environment: dev
components:
  test-component:
    version: "v1.0.0"
    commit: "abc123"
    environment: dev
""")
            
            result = promote_lock_file("dev", "prod", str(manifests_dir))
            
            assert result is True
            target_lock = manifests_dir / "components.lock.prod.yaml"
            assert target_lock.exists()
            
            # Verify content
            with open(target_lock) as f:
                data = yaml.safe_load(f)
                assert data["environment"] == "prod"
                assert "promoted_from" in data
    
    def test_compare_lock_files(self):
        """Test comparing lock files between environments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifests_dir = Path(tmpdir) / "manifests"
            manifests_dir.mkdir()
            
            # Create two lock files
            lock1 = manifests_dir / "components.lock.dev.yaml"
            lock1.write_text("""
generated_at: "2024-01-01T00:00:00Z"
environment: dev
components:
  test-component:
    version: "v1.0.0"
    commit: "abc123"
""")
            
            lock2 = manifests_dir / "components.lock.prod.yaml"
            lock2.write_text("""
generated_at: "2024-01-01T00:00:00Z"
environment: prod
components:
  test-component:
    version: "v2.0.0"
    commit: "def456"
""")
            
            differences = compare_lock_files("dev", "prod", str(manifests_dir))
            
            assert "version_differences" in differences
            assert len(differences["version_differences"]) > 0


