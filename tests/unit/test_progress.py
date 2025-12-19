"""Unit tests for progress indicators."""

import pytest
from meta.utils.progress import ProgressBar, with_progress


class TestProgress:
    """Tests for progress indicators."""
    
    def test_progress_bar(self):
        """Test progress bar rendering."""
        progress = ProgressBar(10, "Test")
        assert progress.total == 10
        assert progress.current == 0
        
        progress.update(5)
        assert progress.current == 5
        
        progress.finish()
        assert progress.current == 10
    
    def test_with_progress(self):
        """Test processing items with progress."""
        items = [1, 2, 3, 4, 5]
        
        def double(x):
            return x * 2
        
        results = with_progress(items, "Doubling", double)
        
        assert len(results) == 5
        assert results == [2, 4, 6, 8, 10]


