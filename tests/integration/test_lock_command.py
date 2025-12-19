"""Integration tests for lock command."""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from meta.cli import app


class TestLockCommand:
    """Integration tests for meta lock command."""
    
    def test_lock_command_generates_file(self):
        """Test that meta lock generates a lock file."""
        runner = CliRunner()
        
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
            
            lock_file = manifests_dir / "components.lock.yaml"
            
            with patch('meta.utils.lock.get_commit_sha_for_ref', return_value="abc123"), \
                 patch('meta.utils.lock.git_available', return_value=True):
                result = runner.invoke(
                    app,
                    ["lock", "--manifests", str(manifests_dir), "--lock-file", str(lock_file)]
                )
                
                assert result.exit_code == 0
                assert lock_file.exists()
    
    def test_lock_validate_command(self):
        """Test that meta lock validate validates lock file."""
        runner = CliRunner()
        
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
            
            # Create matching lock file
            lock_file = manifests_dir / "components.lock.yaml"
            lock_file.write_text("""
generated_at: "2024-01-01T00:00:00Z"
components:
  test-component:
    version: "v1.0.0"
    commit: "abc123"
""")
            
            result = runner.invoke(
                app,
                ["lock", "validate", "--manifests", str(manifests_dir), "--lock-file", str(lock_file)]
            )
            
            assert result.exit_code == 0


