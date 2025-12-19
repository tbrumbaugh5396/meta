"""Integration tests for dependency validation."""

import pytest
import tempfile
from pathlib import Path
from typer.testing import CliRunner
from meta.cli import app


class TestDependencyValidation:
    """Integration tests for dependency validation in validate command."""
    
    def test_validate_detects_missing_dependencies(self):
        """Test that validate command detects missing dependencies."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manifests_dir = Path(tmpdir) / "manifests"
            manifests_dir.mkdir()
            
            # Create components.yaml with missing dependency
            components_yaml = manifests_dir / "components.yaml"
            components_yaml.write_text("""
components:
  component-a:
    repo: "git@github.com:test/a.git"
    version: "v1.0.0"
    type: "bazel"
    depends_on:
      - component-b  # Missing
""")
            
            # Create environments.yaml
            env_yaml = manifests_dir / "environments.yaml"
            env_yaml.write_text("""
environments:
  dev: {}
""")
            
            # Create features.yaml
            features_yaml = manifests_dir / "features.yaml"
            features_yaml.write_text("""
features: {}
""")
            
            with patch('meta.utils.git.git_available', return_value=True), \
                 patch('meta.utils.bazel.bazel_available', return_value=True):
                result = runner.invoke(
                    app,
                    ["validate", "--manifests", str(manifests_dir), "--skip-bazel", "--skip-git"]
                )
                
                # Should fail due to missing dependency
                assert result.exit_code == 1
    
    def test_validate_detects_circular_dependencies(self):
        """Test that validate command detects circular dependencies."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manifests_dir = Path(tmpdir) / "manifests"
            manifests_dir.mkdir()
            
            # Create components.yaml with circular dependency
            components_yaml = manifests_dir / "components.yaml"
            components_yaml.write_text("""
components:
  component-a:
    repo: "git@github.com:test/a.git"
    version: "v1.0.0"
    type: "bazel"
    depends_on:
      - component-b
  component-b:
    repo: "git@github.com:test/b.git"
    version: "v1.0.0"
    type: "bazel"
    depends_on:
      - component-a  # Cycle
""")
            
            # Create environments.yaml
            env_yaml = manifests_dir / "environments.yaml"
            env_yaml.write_text("""
environments:
  dev: {}
""")
            
            # Create features.yaml
            features_yaml = manifests_dir / "features.yaml"
            features_yaml.write_text("""
features: {}
""")
            
            with patch('meta.utils.git.git_available', return_value=True), \
                 patch('meta.utils.bazel.bazel_available', return_value=True):
                result = runner.invoke(
                    app,
                    ["validate", "--manifests", str(manifests_dir), "--skip-bazel", "--skip-git"]
                )
                
                # Should fail due to circular dependency
                assert result.exit_code == 1


