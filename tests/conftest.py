"""Pytest configuration and fixtures."""

import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_manifests():
    """Create a temporary manifests directory with basic structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manifests_dir = Path(tmpdir) / "manifests"
        manifests_dir.mkdir()
        
        # Create basic components.yaml
        components_yaml = manifests_dir / "components.yaml"
        components_yaml.write_text("""
components: {}
""")
        
        # Create basic environments.yaml
        env_yaml = manifests_dir / "environments.yaml"
        env_yaml.write_text("""
environments:
  dev: {}
""")
        
        # Create basic features.yaml
        features_yaml = manifests_dir / "features.yaml"
        features_yaml.write_text("""
features: {}
""")
        
        yield str(manifests_dir)


