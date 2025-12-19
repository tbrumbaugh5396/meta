"""Unit tests for search utilities."""

import pytest
import tempfile
from pathlib import Path
from meta.utils.search import search_components, search_by_dependency, search_by_version


class TestSearch:
    """Tests for search utilities."""
    
    def test_search_components_by_name(self):
        """Test searching components by name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifests_dir = Path(tmpdir) / "manifests"
            manifests_dir.mkdir()
            
            components_yaml = manifests_dir / "components.yaml"
            components_yaml.write_text("""
components:
  frontend-service:
    type: service
    version: v1.0.0
    repo: https://github.com/org/frontend
  backend-api:
    type: api
    version: v2.0.0
    repo: https://github.com/org/backend
""")
            
            results = search_components("frontend", "name", str(manifests_dir))
            assert len(results) == 1
            assert results[0]["name"] == "frontend-service"
    
    def test_search_by_dependency(self):
        """Test searching by dependency."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifests_dir = Path(tmpdir) / "manifests"
            manifests_dir.mkdir()
            
            components_yaml = manifests_dir / "components.yaml"
            components_yaml.write_text("""
components:
  frontend-service:
    type: service
    dependencies: [backend-api]
  backend-api:
    type: api
    dependencies: []
""")
            
            dependents = search_by_dependency("backend-api", str(manifests_dir))
            assert "frontend-service" in dependents
    
    def test_search_by_version(self):
        """Test searching by version pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifests_dir = Path(tmpdir) / "manifests"
            manifests_dir.mkdir()
            
            components_yaml = manifests_dir / "components.yaml"
            components_yaml.write_text("""
components:
  service-v1:
    type: service
    version: v1.0.0
  service-v2:
    type: service
    version: v2.0.0
""")
            
            results = search_by_version("v1", str(manifests_dir))
            assert len(results) == 1
            assert results[0]["name"] == "service-v1"


