"""Unit tests for content-addressed store."""

import pytest
import tempfile
from pathlib import Path
from meta.utils.store import (
    add_to_store, query_store, retrieve_from_store,
    list_store_entries, get_store_stats
)
from meta.utils.content_hash import compute_build_output_hash


class TestStore:
    """Tests for content-addressed store."""
    
    def test_add_and_query_store(self):
        """Test adding and querying store."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_dir = Path(tmpdir) / ".meta-store"
            source_file = Path(tmpdir) / "test.txt"
            source_file.write_text("test content")
            
            content_hash = "abc123def456"
            metadata = {"component": "test-component"}
            
            # Add to store
            result = add_to_store(str(source_file), content_hash, metadata, store_dir=str(store_dir))
            assert result is True
            
            # Query
            entry = query_store(content_hash, store_dir=str(store_dir))
            assert entry is not None
            assert entry["content_hash"] == content_hash
    
    def test_retrieve_from_store(self):
        """Test retrieving from store."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_dir = Path(tmpdir) / ".meta-store"
            source_file = Path(tmpdir) / "test.txt"
            source_file.write_text("test content")
            
            content_hash = "abc123def456"
            add_to_store(str(source_file), content_hash, {}, store_dir=str(store_dir))
            
            # Retrieve
            target_file = Path(tmpdir) / "retrieved.txt"
            result = retrieve_from_store(content_hash, str(target_file), store_dir=str(store_dir))
            assert result is True
            assert target_file.exists()
            assert target_file.read_text() == "test content"
    
    def test_compute_content_hash(self):
        """Test content hash computation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")
            
            hash1 = compute_build_output_hash(str(test_file))
            hash2 = compute_build_output_hash(str(test_file))
            
            # Same content should produce same hash
            assert hash1 == hash2
            
            # Different content should produce different hash
            test_file.write_text("different content")
            hash3 = compute_build_output_hash(str(test_file))
            assert hash1 != hash3


