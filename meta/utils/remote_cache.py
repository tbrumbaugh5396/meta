"""Remote cache/store support (S3, GCS)."""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from meta.utils.logger import log, error, success


class RemoteCacheBackend:
    """Base class for remote cache backends."""
    
    def upload(self, local_path: str, remote_key: str) -> bool:
        """Upload artifact to remote cache."""
        raise NotImplementedError
    
    def download(self, remote_key: str, local_path: str) -> bool:
        """Download artifact from remote cache."""
        raise NotImplementedError
    
    def exists(self, remote_key: str) -> bool:
        """Check if artifact exists in remote cache."""
        raise NotImplementedError
    
    def delete(self, remote_key: str) -> bool:
        """Delete artifact from remote cache."""
        raise NotImplementedError


class S3Backend(RemoteCacheBackend):
    """S3 backend for remote cache."""
    
    def __init__(self, bucket: str, prefix: str = "", region: Optional[str] = None):
        self.bucket = bucket
        self.prefix = prefix.rstrip("/")
        self.region = region or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self._client = None
    
    def _get_client(self):
        """Get boto3 S3 client (lazy import)."""
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client('s3', region_name=self.region)
            except ImportError:
                error("boto3 not installed. Install with: pip install boto3")
                error("S3 remote cache requires boto3. Continuing without remote cache.")
                return None
        return self._client
    
    def _get_key(self, cache_key: str) -> str:
        """Get full S3 key for cache key."""
        if self.prefix:
            return f"{self.prefix}/{cache_key}"
        return cache_key
    
    def upload(self, local_path: str, remote_key: str) -> bool:
        """Upload to S3."""
        try:
            client = self._get_client()
            if client is None:
                return False
            key = self._get_key(remote_key)
            
            local = Path(local_path)
            if local.is_file():
                client.upload_file(str(local), self.bucket, key)
            elif local.is_dir():
                # Upload directory as tar.gz
                import tarfile
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
                    with tarfile.open(tmp.name, 'w:gz') as tar:
                        tar.add(local_path, arcname=local.name)
                    client.upload_file(tmp.name, self.bucket, key)
                    os.unlink(tmp.name)
            else:
                return False
            
            log(f"Uploaded to S3: s3://{self.bucket}/{key}")
            return True
        except Exception as e:
            error(f"Failed to upload to S3: {e}")
            return False
    
    def download(self, remote_key: str, local_path: str) -> bool:
        """Download from S3."""
        try:
            client = self._get_client()
            if client is None:
                return False
            key = self._get_key(remote_key)
            
            local = Path(local_path)
            local.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if it's a tar.gz (directory)
            if key.endswith('.tar.gz'):
                import tarfile
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
                    client.download_file(self.bucket, key, tmp.name)
                    with tarfile.open(tmp.name, 'r:gz') as tar:
                        tar.extractall(local.parent)
                    os.unlink(tmp.name)
            else:
                client.download_file(self.bucket, key, str(local))
            
            log(f"Downloaded from S3: s3://{self.bucket}/{key}")
            return True
        except Exception as e:
            error(f"Failed to download from S3: {e}")
            return False
    
    def exists(self, remote_key: str) -> bool:
        """Check if exists in S3."""
        try:
            client = self._get_client()
            if client is None:
                return False
            key = self._get_key(remote_key)
            client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False
    
    def delete(self, remote_key: str) -> bool:
        """Delete from S3."""
        try:
            client = self._get_client()
            if client is None:
                return False
            key = self._get_key(remote_key)
            client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except Exception as e:
            error(f"Failed to delete from S3: {e}")
            return False


class GCSBackend(RemoteCacheBackend):
    """Google Cloud Storage backend for remote cache."""
    
    def __init__(self, bucket: str, prefix: str = ""):
        self.bucket = bucket
        self.prefix = prefix.rstrip("/")
        self._client = None
    
    def _get_client(self):
        """Get google-cloud-storage client (lazy import)."""
        if self._client is None:
            try:
                from google.cloud import storage
                self._client = storage.Client()
            except ImportError:
                error("google-cloud-storage not installed. Install with: pip install google-cloud-storage")
                error("GCS remote cache requires google-cloud-storage. Continuing without remote cache.")
                return None
        return self._client
    
    def _get_blob_name(self, cache_key: str) -> str:
        """Get full blob name for cache key."""
        if self.prefix:
            return f"{self.prefix}/{cache_key}"
        return cache_key
    
    def upload(self, local_path: str, remote_key: str) -> bool:
        """Upload to GCS."""
        try:
            client = self._get_client()
            if client is None:
                return False
            bucket = client.bucket(self.bucket)
            blob_name = self._get_blob_name(remote_key)
            blob = bucket.blob(blob_name)
            
            local = Path(local_path)
            if local.is_file():
                blob.upload_from_filename(str(local))
            elif local.is_dir():
                # Upload directory as tar.gz
                import tarfile
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
                    with tarfile.open(tmp.name, 'w:gz') as tar:
                        tar.add(local_path, arcname=local.name)
                    blob.upload_from_filename(tmp.name)
                    os.unlink(tmp.name)
            else:
                return False
            
            log(f"Uploaded to GCS: gs://{self.bucket}/{blob_name}")
            return True
        except Exception as e:
            error(f"Failed to upload to GCS: {e}")
            return False
    
    def download(self, remote_key: str, local_path: str) -> bool:
        """Download from GCS."""
        try:
            client = self._get_client()
            if client is None:
                return False
            bucket = client.bucket(self.bucket)
            blob_name = self._get_blob_name(remote_key)
            blob = bucket.blob(blob_name)
            
            local = Path(local_path)
            local.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if it's a tar.gz (directory)
            if blob_name.endswith('.tar.gz'):
                import tarfile
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
                    blob.download_to_filename(tmp.name)
                    with tarfile.open(tmp.name, 'r:gz') as tar:
                        tar.extractall(local.parent)
                    os.unlink(tmp.name)
            else:
                blob.download_to_filename(str(local))
            
            log(f"Downloaded from GCS: gs://{self.bucket}/{blob_name}")
            return True
        except Exception as e:
            error(f"Failed to download from GCS: {e}")
            return False
    
    def exists(self, remote_key: str) -> bool:
        """Check if exists in GCS."""
        try:
            client = self._get_client()
            if client is None:
                return False
            bucket = client.bucket(self.bucket)
            blob_name = self._get_blob_name(remote_key)
            blob = bucket.blob(blob_name)
            return blob.exists()
        except Exception:
            return False
    
    def delete(self, remote_key: str) -> bool:
        """Delete from GCS."""
        try:
            client = self._get_client()
            if client is None:
                return False
            bucket = client.bucket(self.bucket)
            blob_name = self._get_blob_name(remote_key)
            blob = bucket.blob(blob_name)
            blob.delete()
            return True
        except Exception as e:
            error(f"Failed to delete from GCS: {e}")
            return False


def create_remote_backend(remote_url: str) -> Optional[RemoteCacheBackend]:
    """Create remote backend from URL."""
    if remote_url.startswith("s3://"):
        # s3://bucket-name/path
        parts = remote_url[5:].split("/", 1)
        bucket = parts[0]
        prefix = parts[1] if len(parts) > 1 else ""
        return S3Backend(bucket, prefix)
    elif remote_url.startswith("gs://"):
        # gs://bucket-name/path
        parts = remote_url[5:].split("/", 1)
        bucket = parts[0]
        prefix = parts[1] if len(parts) > 1 else ""
        return GCSBackend(bucket, prefix)
    else:
        error(f"Unsupported remote URL format: {remote_url}")
        return None

