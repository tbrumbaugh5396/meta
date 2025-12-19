"""Unit tests for alias utilities."""

import pytest
import tempfile
from pathlib import Path
from meta.utils.aliases import (
    create_alias, delete_alias, list_aliases, resolve_alias, load_aliases, save_aliases
)


class TestAliases:
    """Tests for alias utilities."""
    
    def test_create_and_resolve_alias(self):
        """Test creating and resolving an alias."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import meta.utils.aliases as alias_module
            original_path = alias_module.ALIASES_FILE
            alias_module.ALIASES_FILE = Path(tmpdir) / ".meta" / "aliases.yaml"
            
            try:
                create_alias("comp", "web", "frontend-service")
                result = resolve_alias("comp", "web")
                assert result == "frontend-service"
            finally:
                alias_module.ALIASES_FILE = original_path
    
    def test_delete_alias(self):
        """Test deleting an alias."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import meta.utils.aliases as alias_module
            original_path = alias_module.ALIASES_FILE
            alias_module.ALIASES_FILE = Path(tmpdir) / ".meta" / "aliases.yaml"
            
            try:
                create_alias("comp", "web", "frontend-service")
                assert resolve_alias("comp", "web") == "frontend-service"
                
                delete_alias("comp", "web")
                assert resolve_alias("comp", "web") is None
            finally:
                alias_module.ALIASES_FILE = original_path
    
    def test_list_aliases(self):
        """Test listing aliases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import meta.utils.aliases as alias_module
            original_path = alias_module.ALIASES_FILE
            alias_module.ALIASES_FILE = Path(tmpdir) / ".meta" / "aliases.yaml"
            
            try:
                create_alias("comp", "web", "frontend-service")
                create_alias("env", "prod", "production")
                
                all_aliases = list_aliases()
                assert len(all_aliases) == 2
                
                comp_aliases = list_aliases("comp")
                assert len(comp_aliases) == 1
                assert "web" in comp_aliases
            finally:
                alias_module.ALIASES_FILE = original_path


