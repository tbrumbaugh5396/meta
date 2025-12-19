"""Unit tests for rollback utilities."""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch
from meta.utils.rollback import (
    find_rollback_targets,
    rollback_component,
    rollback_from_lock_file,
    create_rollback_snapshot,
    RollbackTarget
)


class TestRollback:
    """Tests for rollback utilities."""
    
    def test_find_rollback_targets(self):
        """Test finding rollback targets."""
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
            
            # Create lock file
            lock_file = manifests_dir / "components.lock.yaml"
            lock_file.write_text("""
generated_at: "2024-01-01T00:00:00Z"
components:
  test-component:
    version: "v1.0.0"
    commit: "abc123def456"
""")
            
            with patch('meta.utils.rollback.get_current_version', return_value="v1.0.0"):
                targets = find_rollback_targets("test-component", str(manifests_dir))
                
                assert len(targets) > 0
                assert any(t.component == "test-component" for t in targets)
    
    def test_rollback_component(self):
        """Test rolling back a component."""
        with tempfile.TemporaryDirectory() as tmpdir:
            comp_dir = Path(tmpdir) / "test-component"
            comp_dir.mkdir()
            
            target = RollbackTarget("test-component", version="v1.0.0")
            
            with patch('meta.utils.rollback.checkout_version', return_value=True):
                result = rollback_component("test-component", target)
                assert result is True
    
    def test_create_rollback_snapshot(self):
        """Test creating rollback snapshot."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifests_dir = Path(tmpdir) / "manifests"
            manifests_dir.mkdir()
            
            components_yaml = manifests_dir / "components.yaml"
            components_yaml.write_text("""
components:
  test-component:
    repo: "git@github.com:test/test.git"
    version: "v1.0.0"
    type: "bazel"
""")
            
            comp_dir = Path(tmpdir) / "components" / "test-component"
            comp_dir.mkdir(parents=True)
            
            snapshot_file = Path(tmpdir) / "snapshot.yaml"
            
            with patch('meta.utils.rollback.get_current_version', return_value="v1.0.0"), \
                 patch('meta.utils.rollback.get_commit_sha', return_value="abc123"):
                result = create_rollback_snapshot(
                    components=["test-component"],
                    manifests_dir=str(manifests_dir),
                    snapshot_file=str(snapshot_file)
                )
                
                assert result is True
                assert snapshot_file.exists()
                
                # Verify snapshot content
                with open(snapshot_file) as f:
                    data = yaml.safe_load(f)
                    assert "test-component" in data["components"]


