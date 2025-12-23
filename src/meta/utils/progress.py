"""Progress indicators for long-running operations."""

from typing import Optional, Callable, Any
from meta.utils.logger import log


class ProgressBar:
    """Simple progress bar implementation."""
    
    def __init__(self, total: int, description: str = "Progress"):
        self.total = total
        self.current = 0
        self.description = description
        self.width = 50
    
    def update(self, n: int = 1):
        """Update progress by n."""
        self.current = min(self.current + n, self.total)
        self._render()
    
    def _render(self):
        """Render progress bar."""
        if self.total == 0:
            percent = 100
        else:
            percent = int((self.current / self.total) * 100)
        
        filled = int((self.current / self.total) * self.width) if self.total > 0 else self.width
        bar = "█" * filled + "░" * (self.width - filled)
        
        print(f"\r{self.description}: [{bar}] {percent}% ({self.current}/{self.total})", end="", flush=True)
    
    def finish(self):
        """Finish progress bar."""
        self.current = self.total
        self._render()
        print()  # New line


def with_progress(items: list, description: str = "Processing", 
                 callback: Optional[Callable] = None) -> list:
    """Process items with progress bar."""
    progress = ProgressBar(len(items), description)
    results = []
    
    try:
        for item in items:
            if callback:
                result = callback(item)
                results.append(result)
            else:
                results.append(item)
            progress.update(1)
    finally:
        progress.finish()
    
    return results


