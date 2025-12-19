"""Unit tests for remote cache backends."""

import pytest
from unittest.mock import MagicMock, patch
from meta.utils.remote_cache import S3Backend, GCSBackend, create_remote_backend


class TestRemoteCache:
    """Tests for remote cache backends."""
    
    def test_create_s3_backend(self):
        """Test creating S3 backend."""
        backend = create_remote_backend("s3://my-bucket/cache")
        assert isinstance(backend, S3Backend)
        assert backend.bucket == "my-bucket"
        assert backend.prefix == "cache"
    
    def test_create_gcs_backend(self):
        """Test creating GCS backend."""
        backend = create_remote_backend("gs://my-bucket/cache")
        assert isinstance(backend, GCSBackend)
        assert backend.bucket == "my-bucket"
        assert backend.prefix == "cache"
    
    def test_s3_backend_key_generation(self):
        """Test S3 key generation."""
        backend = S3Backend("my-bucket", "cache")
        key = backend._get_key("abc123")
        assert key == "cache/abc123"
        
        backend_no_prefix = S3Backend("my-bucket")
        key = backend_no_prefix._get_key("abc123")
        assert key == "abc123"
    
    def test_gcs_backend_blob_name(self):
        """Test GCS blob name generation."""
        backend = GCSBackend("my-bucket", "cache")
        blob_name = backend._get_blob_name("abc123")
        assert blob_name == "cache/abc123"


