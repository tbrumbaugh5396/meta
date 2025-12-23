"""Unit tests for sync utilities."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from meta.utils.sync import sync_component, sync_all_components


class TestSync:
    """Tests for sync utilities."""
    
    @patch('meta.utils.sync.get_current_version')
    @patch('meta.utils.sync.pull_latest')
    @patch('meta.utils.sync.checkout_version')
    @patch('meta.utils.sync.get_environment_config')
    def test_sync_component(self, mock_get_env, mock_checkout, mock_pull, mock_get_version):
        """Test syncing a component."""
        mock_get_version.return_value = "v1.0.0"
        mock_pull.return_value = True
        mock_checkout.return_value = True
        mock_get_env.return_value = {
            "components": {
                "test-component": {
                    "version": "v2.0.0"
                }
            }
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manifests_dir = Path(tmpdir) / "manifests"
            manifests_dir.mkdir()
            
            components_yaml = manifests_dir / "components.yaml"
            components_yaml.write_text("""
components:
  test-component:
    type: service
    version: v2.0.0
""")
            
            environments_yaml = manifests_dir / "environments.yaml"
            environments_yaml.write_text("""
environments:
  dev:
    components:
      test-component:
        version: v2.0.0
""")
            
            result = sync_component("test-component", "dev", str(manifests_dir))
            assert result is True
            mock_checkout.assert_called_once()


