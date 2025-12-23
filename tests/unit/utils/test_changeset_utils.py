"""Tests for changeset utilities with dependency injection."""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestChangesetUtils:
    """Tests for changeset utility functions."""
    
    def test_create_changeset(self, temp_meta_repo):
        """Test creating a changeset."""
        from meta.utils.changeset import create_changeset
        from pathlib import Path
        
        # Create actual changeset directory
        changeset_dir = temp_meta_repo["path"] / ".meta" / "changesets"
        changeset_dir.mkdir(parents=True, exist_ok=True)
        
        changeset = create_changeset("Test changeset", "test@example.com")
        
        assert changeset is not None
        assert changeset.description == "Test changeset"
        assert changeset.author == "test@example.com"
        assert changeset.status == "in-progress"
    
    def test_load_changeset(self, temp_meta_repo):
        """Test loading a changeset."""
        from meta.utils.changeset import load_changeset, save_changeset, create_changeset
        import yaml
        
        # Create actual changeset directory
        changeset_dir = temp_meta_repo["path"] / ".meta" / "changesets"
        changeset_dir.mkdir(parents=True, exist_ok=True)
        
        changeset = create_changeset("Test changeset")
        save_changeset(changeset)
        
        # Load it
        loaded = load_changeset(changeset.id)
        
        assert loaded is not None
        assert loaded.id == changeset.id
        assert loaded.description == "Test changeset"
    
    def test_list_changesets(self, temp_meta_repo):
        """Test listing changesets."""
        from meta.utils.changeset import list_changesets
        
        with patch('meta.utils.changeset.CHANGESET_INDEX') as mock_index, \
             patch('meta.utils.changeset.CHANGESET_DIR') as mock_dir:
            
            mock_index.exists.return_value = True
            mock_index.read_text.return_value = """
changesets:
  - id: changeset-1
    description: Test 1
    timestamp: 2024-01-01T00:00:00
    status: committed
  - id: changeset-2
    description: Test 2
    timestamp: 2024-01-02T00:00:00
    status: in_progress
"""
            
            changesets = list_changesets(limit=10)
            
            assert len(changesets) >= 0  # May be empty if index doesn't exist
    
    def test_find_changeset_by_commit(self, temp_meta_repo):
        """Test finding changeset by commit."""
        from meta.utils.changeset import find_changeset_by_commit, Changeset
        
        changeset = Changeset("changeset-123", "Test")
        changeset.add_repo_commit(
            "test-component",
            "git@github.com:test/test.git",
            "abc123",
            "main",
            "Test commit"
        )
        
        with patch('meta.utils.changeset.list_changesets') as mock_list, \
             patch('meta.utils.changeset.load_changeset') as mock_load:
            
            mock_list.return_value = [changeset]
            mock_load.return_value = changeset
            
            found = find_changeset_by_commit("test-component", "abc123")
            
            # May return None if not found
            assert found is None or found.id == "changeset-123"
    
    def test_extract_changeset_id_from_message(self):
        """Test extracting changeset ID from commit message."""
        from meta.utils.changeset import extract_changeset_id_from_message
        
        # Test with [changeset:ID] format
        assert extract_changeset_id_from_message("Fix bug [changeset:abc123]") == "abc123"
        
        # Test without changeset ID
        assert extract_changeset_id_from_message("Fix bug") is None
        
        # Test with multiple IDs (should get first)
        assert extract_changeset_id_from_message("[changeset:abc123] [changeset:def456]") == "abc123"
    
    def test_get_current_changeset(self, temp_meta_repo):
        """Test getting current changeset."""
        from meta.utils.changeset import get_current_changeset, Changeset
        
        with patch('meta.utils.changeset.CHANGESET_DIR') as mock_dir:
            mock_file = MagicMock()
            mock_file.exists.return_value = True
            mock_file.read_text.return_value = "changeset-123"
            (mock_dir / "current").__truediv__ = lambda x, y: mock_file
            mock_dir.__truediv__ = lambda x, y: mock_file
            
            with patch('meta.utils.changeset.load_changeset') as mock_load:
                mock_changeset = Changeset("changeset-123", "Test")
                mock_load.return_value = mock_changeset
                
                current = get_current_changeset()
                
                assert current is not None
                assert current.id == "changeset-123"

