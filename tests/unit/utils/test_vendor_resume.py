"""Tests for vendor resume utilities."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json
from meta.utils.vendor_resume import (
    create_checkpoint,
    load_checkpoint,
    resume_conversion,
    list_checkpoints,
    get_latest_checkpoint
)


class TestVendorResume:
    """Test vendor resume utilities."""
    
    @patch("meta.utils.vendor_resume.get_components")
    @patch("meta.utils.vendor_resume.find_meta_repo_root")
    def test_create_checkpoint(self, mock_find_root, mock_get_components, temp_meta_repo):
        """Test creating a checkpoint."""
        mock_find_root.return_value = temp_meta_repo["path"]
        mock_get_components.return_value = {
            "test-component": {
                "repo": "git@github.com:test/test.git",
                "version": "v1.0.0"
            }
        }
        
        checkpoint = create_checkpoint("vendored", str(temp_meta_repo["manifests"]))
        
        assert checkpoint is not None
        assert checkpoint.checkpoint_id is not None
        assert checkpoint.target_mode == "vendored"
        assert "test-component" in checkpoint.pending_components or "test-component" in checkpoint.completed_components
    
    def test_load_checkpoint(self, temp_meta_repo):
        """Test loading a checkpoint."""
        checkpoint_dir = temp_meta_repo["path"] / ".meta" / "resume" / "checkpoint-123"
        checkpoint_dir.mkdir(parents=True)
        
        checkpoint_data = {
            'checkpoint_id': 'checkpoint-123',
            'target_mode': 'vendored',
            'manifests_dir': 'manifests',
            'created_at': '2024-01-15T12:00:00Z',
            'completed_components': [],
            'failed_components': [],
            'pending_components': ['test-component']
        }
        
        (checkpoint_dir / "checkpoint.json").write_text(json.dumps(checkpoint_data))
        
        with patch("meta.utils.vendor_resume.RESUME_DIR", checkpoint_dir.parent):
            checkpoint = load_checkpoint("checkpoint-123")
            assert checkpoint is not None
            assert checkpoint.checkpoint_id == "checkpoint-123"
    
    def test_checkpoint_mark_completed(self, temp_meta_repo):
        """Test marking component as completed."""
        checkpoint_dir = temp_meta_repo["path"] / ".meta" / "resume" / "checkpoint-123"
        checkpoint_dir.mkdir(parents=True)
        
        with patch("meta.utils.vendor_resume.RESUME_DIR", checkpoint_dir.parent):
            checkpoint = create_checkpoint("vendored", "manifests")
            checkpoint.pending_components = ["test-component"]
            
            checkpoint.mark_completed("test-component")
            
            assert "test-component" in checkpoint.completed_components
            assert "test-component" not in checkpoint.pending_components
    
    def test_checkpoint_mark_failed(self, temp_meta_repo):
        """Test marking component as failed."""
        checkpoint_dir = temp_meta_repo["path"] / ".meta" / "resume" / "checkpoint-123"
        checkpoint_dir.mkdir(parents=True)
        
        with patch("meta.utils.vendor_resume.RESUME_DIR", checkpoint_dir.parent):
            checkpoint = create_checkpoint("vendored", "manifests")
            checkpoint.pending_components = ["test-component"]
            
            checkpoint.mark_failed("test-component")
            
            assert "test-component" in checkpoint.failed_components
            assert "test-component" not in checkpoint.pending_components
    
    def test_checkpoint_get_progress(self, temp_meta_repo):
        """Test getting checkpoint progress."""
        checkpoint_dir = temp_meta_repo["path"] / ".meta" / "resume" / "checkpoint-123"
        checkpoint_dir.mkdir(parents=True)
        
        with patch("meta.utils.vendor_resume.RESUME_DIR", checkpoint_dir.parent):
            checkpoint = create_checkpoint("vendored", "manifests")
            checkpoint.completed_components = {"comp1"}
            checkpoint.pending_components = ["comp2", "comp3"]
            
            progress = checkpoint.get_progress()
            
            assert progress['total'] == 3
            assert progress['completed'] == 1
            assert progress['pending'] == 2
    
    @patch("meta.utils.vendor_resume.load_checkpoint")
    def test_resume_conversion(self, mock_load, temp_meta_repo):
        """Test resuming conversion."""
        mock_checkpoint = MagicMock()
        mock_checkpoint.checkpoint_id = "checkpoint-123"
        mock_checkpoint.completed_components = set()
        mock_checkpoint.failed_components = set()
        mock_checkpoint.pending_components = ["test-component"]
        mock_checkpoint.get_progress.return_value = {
            'total': 1,
            'completed': 0,
            'failed': 0,
            'pending': 1,
            'progress_percent': 0.0
        }
        mock_load.return_value = mock_checkpoint
        
        checkpoint = resume_conversion("checkpoint-123", skip_completed=True, retry_failed=True)
        
        assert checkpoint is not None
        assert checkpoint.checkpoint_id == "checkpoint-123"
    
    def test_list_checkpoints(self, temp_meta_repo):
        """Test listing checkpoints."""
        checkpoint_dir = temp_meta_repo["path"] / ".meta" / "resume"
        checkpoint_dir.mkdir(parents=True)
        
        checkpoint1 = checkpoint_dir / "checkpoint-1"
        checkpoint1.mkdir()
        (checkpoint1 / "checkpoint.json").write_text(json.dumps({
            'checkpoint_id': 'checkpoint-1',
            'target_mode': 'vendored',
            'created_at': '2024-01-15T12:00:00Z'
        }))
        
        with patch("meta.utils.vendor_resume.RESUME_DIR", checkpoint_dir):
            checkpoints = list_checkpoints()
            assert len(checkpoints) > 0

