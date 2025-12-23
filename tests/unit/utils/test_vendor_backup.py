"""Tests for vendor backup utilities."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json
from meta.utils.vendor_backup import (
    create_backup,
    list_backups,
    restore_backup,
    get_latest_backup
)


class TestVendorBackup:
    """Test vendor backup utilities."""
    
    @patch("meta.utils.vendor_backup.find_meta_repo_root")
    @patch("shutil.copytree")
    @patch("builtins.open", create=True)
    def test_create_backup(self, mock_open, mock_copytree, mock_find_root, temp_meta_repo):
        """Test creating a backup."""
        mock_find_root.return_value = temp_meta_repo["path"]
        
        # Create actual backup directory structure
        backup_dir = temp_meta_repo["path"] / ".meta" / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / "test-backup"
        
        # Mock file writing
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        with patch("meta.utils.vendor_backup.BACKUP_DIR", backup_dir):
            result = create_backup("test-backup", include_components=True)
            
            assert result is not None
    
    @patch("meta.utils.vendor_backup.find_meta_repo_root")
    @patch("shutil.copytree")
    @patch("builtins.open", create=True)
    def test_create_backup_no_components(self, mock_open, mock_copytree, mock_find_root, temp_meta_repo):
        """Test creating backup without components."""
        mock_find_root.return_value = temp_meta_repo["path"]
        
        # Create actual backup directory structure
        backup_dir = temp_meta_repo["path"] / ".meta" / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock file writing
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        with patch("meta.utils.vendor_backup.BACKUP_DIR", backup_dir):
            result = create_backup("test-backup", include_components=False)
            
            assert result is not None
    
    def test_list_backups_empty(self):
        """Test listing backups when none exist."""
        with patch("meta.utils.vendor_backup.BACKUP_DIR") as mock_dir:
            mock_dir.exists.return_value = False
            backups = list_backups()
            assert backups == []
    
    @patch("meta.utils.vendor_backup.BACKUP_DIR")
    def test_list_backups(self, mock_backup_dir, temp_meta_repo):
        """Test listing backups."""
        backup_dir = temp_meta_repo["path"] / ".meta" / "backups" / "backup1"
        backup_dir.mkdir(parents=True)
        
        metadata = {
            'backup_name': 'backup1',
            'created_at': '2024-01-15T12:00:00Z',
            'includes_components': True
        }
        (backup_dir / "backup_metadata.json").write_text(json.dumps(metadata))
        
        with patch("meta.utils.vendor_backup.BACKUP_DIR", backup_dir.parent):
            backups = list_backups()
            assert len(backups) > 0
    
    @patch("meta.utils.vendor_backup.find_meta_repo_root")
    @patch("shutil.copytree")
    @patch("shutil.rmtree")
    def test_restore_backup(self, mock_rmtree, mock_copytree, mock_find_root, temp_meta_repo):
        """Test restoring from backup."""
        mock_find_root.return_value = temp_meta_repo["path"]
        
        # Create backup first
        backup_dir = temp_meta_repo["path"] / ".meta" / "backups" / "test-backup"
        backup_dir.mkdir(parents=True)
        (backup_dir / "manifests").mkdir()
        (backup_dir / "backup_metadata.json").write_text(json.dumps({
            'backup_name': 'test-backup',
            'created_at': '2024-01-15T12:00:00Z'
        }))
        
        with patch("meta.utils.vendor_backup.BACKUP_DIR", backup_dir.parent):
            result = restore_backup("test-backup", restore_components=True)
            assert result is True
    
    def test_get_latest_backup(self):
        """Test getting latest backup."""
        # list_backups sorts by created_at desc, so backup2 (newer) comes first
        backups = [
            {'backup_name': 'backup2', 'created_at': '2024-01-16T12:00:00Z'},
            {'backup_name': 'backup1', 'created_at': '2024-01-15T12:00:00Z'}
        ]
        with patch("meta.utils.vendor_backup.list_backups", return_value=backups):
            latest = get_latest_backup()
            assert latest is not None
            # Latest should be the first one (sorted by created_at desc)
            assert latest['backup_name'] == 'backup2'

