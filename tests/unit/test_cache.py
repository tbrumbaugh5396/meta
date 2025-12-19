"""Unit tests for cache management."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
from meta.utils.cache import (
    store_artifact, retrieve_artifact, invalidate_cache,
    list_cache_entries, get_cache_stats, get_cache_dir
)
from meta.utils.cache_keys import compute_component_cache_key, get_cache_path


class TestCache:
    """Tests for cache management."""
    
    def test_store_and_retrieve_artifact(self):
        """Test storing and retrieving artifacts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".meta-cache"
            source_file = Path(tmpdir) / "test.txt"
            source_file.write_text("test content")
            
            cache_key = "test123456789"
            
            # Store
            result = store_artifact(cache_key, str(source_file), "test-component", cache_dir=str(cache_dir))
            assert result is True
            
            # Retrieve
            target_file = Path(tmpdir) / "retrieved.txt"
            result = retrieve_artifact(cache_key, str(target_file), cache_dir=str(cache_dir))
            assert result is True
            assert target_file.exists()
            assert target_file.read_text() == "test content"
    
    def test_invalidate_cache(self):
        """Test cache invalidation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".meta-cache"
            source_file = Path(tmpdir) / "test.txt"
            source_file.write_text("test")
            
            cache_key = "test123456789"
            store_artifact(cache_key, str(source_file), "test-component", cache_dir=str(cache_dir))
            
            # Invalidate
            removed = invalidate_cache(cache_key=cache_key, cache_dir=str(cache_dir))
            assert removed == 1
    
    def test_compute_cache_key(self):
        """Test cache key computation."""
        component_data = {
            "version": "v1.0.0",
            "type": "bazel",
            "build_target": "//test:all"
        }
        
        cache_key = compute_component_cache_key("test-component", component_data, ["dep1"], "manifests")
        
        assert cache_key is not None
        assert len(cache_key) == 64  # SHA256 hex length


