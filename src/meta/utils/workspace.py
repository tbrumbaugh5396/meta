"""Multi-tenant workspace utilities."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from meta.utils.logger import log, error
from meta.utils.config import get_config


WORKSPACE_CONFIG_FILE = ".meta/workspace.yaml"


class WorkspaceManager:
    """Manages multiple workspaces."""
    
    def __init__(self, config_file: str = WORKSPACE_CONFIG_FILE):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.workspaces: Dict[str, Any] = self._load_workspaces()
        self.current_workspace: Optional[str] = None
    
    def _load_workspaces(self) -> Dict[str, Any]:
        """Load workspace configuration."""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file) as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            error(f"Failed to load workspaces: {e}")
            return {}
    
    def _save_workspaces(self):
        """Save workspace configuration."""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.workspaces, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            error(f"Failed to save workspaces: {e}")
    
    def create_workspace(self, name: str, manifests_dir: Optional[str] = None) -> bool:
        """Create a new workspace."""
        if name in self.workspaces:
            error(f"Workspace {name} already exists")
            return False
        
        self.workspaces[name] = {
            "manifests_dir": manifests_dir or f"manifests-{name}",
            "components_dir": f"components-{name}",
            "created_at": yaml.safe_dump({"timestamp": "now"})  # Simplified
        }
        
        self._save_workspaces()
        return True
    
    def switch_workspace(self, name: str) -> bool:
        """Switch to a workspace."""
        if name not in self.workspaces:
            error(f"Workspace {name} not found")
            return False
        
        self.current_workspace = name
        # Update config
        config = get_config()
        workspace = self.workspaces[name]
        config.set("manifests_dir", workspace.get("manifests_dir", "manifests"))
        return True
    
    def get_current_workspace(self) -> Optional[str]:
        """Get current workspace name."""
        return self.current_workspace
    
    def list_workspaces(self) -> Dict[str, Any]:
        """List all workspaces."""
        return self.workspaces
    
    def delete_workspace(self, name: str) -> bool:
        """Delete a workspace."""
        if name not in self.workspaces:
            error(f"Workspace {name} not found")
            return False
        
        del self.workspaces[name]
        self._save_workspaces()
        return True


def get_workspace_manager() -> WorkspaceManager:
    """Get workspace manager instance."""
    return WorkspaceManager()


