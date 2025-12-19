"""Unit tests for templates library utilities."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from meta.utils.templates_library import TemplateLibrary, get_template_library


class TestTemplateLibrary:
    """Tests for TemplateLibrary."""
    
    def test_list_templates_empty(self):
        """Test listing templates when none exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            library = TemplateLibrary()
            library.templates_dir = Path(tmpdir) / ".meta" / "templates"
            library.index_file = library.templates_dir / "index.yaml"
            library.templates_dir.mkdir(parents=True, exist_ok=True)
            
            templates = library.list_templates()
            assert templates == []
    
    def test_install_template(self):
        """Test installing a template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            library = TemplateLibrary()
            library.templates_dir = Path(tmpdir) / ".meta" / "templates"
            library.index_file = library.templates_dir / "index.yaml"
            library.templates_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a source template directory
            source_dir = Path(tmpdir) / "source_template"
            source_dir.mkdir()
            (source_dir / "template.yaml").write_text("name: test")
            
            result = library.install_template("test-template", str(source_dir), "general", "Test template")
            assert result is True
            
            templates = library.list_templates()
            assert len(templates) == 1
            assert templates[0]["name"] == "test-template"
    
    def test_get_template(self):
        """Test getting a template by name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            library = TemplateLibrary()
            library.templates_dir = Path(tmpdir) / ".meta" / "templates"
            library.index_file = library.templates_dir / "index.yaml"
            library.templates_dir.mkdir(parents=True, exist_ok=True)
            
            # Install a template
            source_dir = Path(tmpdir) / "source_template"
            source_dir.mkdir()
            library.install_template("test-template", str(source_dir), "general")
            
            template = library.get_template("test-template")
            assert template is not None
            assert template["name"] == "test-template"
            
            # Non-existent template
            template = library.get_template("non-existent")
            assert template is None
    
    def test_search_templates(self):
        """Test searching templates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            library = TemplateLibrary()
            library.templates_dir = Path(tmpdir) / ".meta" / "templates"
            library.index_file = library.templates_dir / "index.yaml"
            library.templates_dir.mkdir(parents=True, exist_ok=True)
            
            # Install templates
            source_dir = Path(tmpdir) / "source_template"
            source_dir.mkdir()
            library.install_template("python-service", str(source_dir), "service", "Python service template")
            library.install_template("node-app", str(source_dir), "app", "Node.js app template")
            
            results = library.search_templates("python")
            assert len(results) == 1
            assert results[0]["name"] == "python-service"
            
            results = library.search_templates("template")
            assert len(results) == 2


