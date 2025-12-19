"""Component history utilities."""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from meta.utils.logger import log, error
from meta.utils.git import get_commit_sha, get_current_version


HISTORY_DIR = Path(".meta/history")


class ComponentHistory:
    """Manages component history."""
    
    def __init__(self):
        self.history_dir = HISTORY_DIR
        self.history_dir.mkdir(parents=True, exist_ok=True)
    
    def record_action(
        self,
        component: str,
        action: str,
        version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Record a component action."""
        history_file = self.history_dir / f"{component}.json"
        
        # Load existing history
        history = []
        if history_file.exists():
            try:
                with open(history_file) as f:
                    history = json.load(f)
            except:
                history = []
        
        # Add new entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "version": version or get_current_version(f"components/{component}"),
            "metadata": metadata or {}
        }
        
        history.append(entry)
        
        # Keep only last 1000 entries
        history = history[-1000:]
        
        # Save
        try:
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
            return True
        except Exception as e:
            error(f"Failed to record history: {e}")
            return False
    
    def get_history(
        self,
        component: str,
        limit: int = 50,
        action_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get component history."""
        history_file = self.history_dir / f"{component}.json"
        
        if not history_file.exists():
            return []
        
        try:
            with open(history_file) as f:
                history = json.load(f)
            
            # Filter by action if specified
            if action_filter:
                history = [h for h in history if h.get("action") == action_filter]
            
            # Limit
            return history[-limit:]
        except:
            return []
    
    def get_all_history(self, limit: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        """Get history for all components."""
        all_history = {}
        
        for history_file in self.history_dir.glob("*.json"):
            component = history_file.stem
            all_history[component] = self.get_history(component, limit)
        
        return all_history
    
    def clear_history(self, component: Optional[str] = None) -> bool:
        """Clear history."""
        if component:
            history_file = self.history_dir / f"{component}.json"
            if history_file.exists():
                history_file.unlink()
        else:
            # Clear all
            for history_file in self.history_dir.glob("*.json"):
                history_file.unlink()
        
        return True


def get_component_history() -> ComponentHistory:
    """Get component history instance."""
    return ComponentHistory()


