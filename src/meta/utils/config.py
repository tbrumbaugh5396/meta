"""Configuration management utilities."""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from meta.utils.logger import log, error


CONFIG_FILENAME = ".meta/config.yaml"
GLOBAL_CONFIG_PATH = Path.home() / ".meta" / "config.yaml"


class Config:
    """Configuration manager."""
    
    def __init__(self, project_dir: Optional[str] = None):
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.project_config_path = self.project_dir / CONFIG_FILENAME
        self.global_config_path = GLOBAL_CONFIG_PATH
        
        self._project_config: Optional[Dict[str, Any]] = None
        self._global_config: Optional[Dict[str, Any]] = None
    
    def _load_config(self, path: Path) -> Dict[str, Any]:
        """Load config from file."""
        if not path.exists():
            return {}
        
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            error(f"Failed to load config from {path}: {e}")
            return {}
    
    def _get_project_config(self) -> Dict[str, Any]:
        """Get project config."""
        if self._project_config is None:
            self._project_config = self._load_config(self.project_config_path)
        return self._project_config
    
    def _get_global_config(self) -> Dict[str, Any]:
        """Get global config."""
        if self._global_config is None:
            self._global_config = self._load_config(self.global_config_path)
        return self._global_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value (project overrides global)."""
        # Check environment variable first
        env_key = f"META_{key.upper().replace('.', '_')}"
        if env_key in os.environ:
            return os.environ[env_key]
        
        # Check project config
        project_config = self._get_project_config()
        if key in project_config:
            return project_config[key]
        
        # Check global config
        global_config = self._get_global_config()
        if key in global_config:
            return global_config[key]
        
        return default
    
    def set(self, key: str, value: Any, global_config: bool = False) -> bool:
        """Set config value."""
        if global_config:
            config_path = self.global_config_path
            config = self._get_global_config()
        else:
            config_path = self.project_config_path
            config = self._get_project_config()
        
        # Set value
        keys = key.split('.')
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        
        # Save to file
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            # Reload
            if global_config:
                self._global_config = config
            else:
                self._project_config = config
            
            return True
        except Exception as e:
            error(f"Failed to save config to {config_path}: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """Get all config (merged, project overrides global)."""
        merged = {}
        merged.update(self._get_global_config())
        merged.update(self._get_project_config())
        return merged
    
    def init_config(self, global_config: bool = False) -> bool:
        """Initialize config file with defaults."""
        defaults = {
            "default_env": "dev",
            "manifests_dir": "manifests",
            "parallel_jobs": 4,
            "show_progress": True,
            "log_level": "INFO",
            "remote_cache": None,
            "remote_store": None
        }
        
        if global_config:
            config_path = self.global_config_path
        else:
            config_path = self.project_config_path
        
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                yaml.dump(defaults, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            error(f"Failed to initialize config: {e}")
            return False


def get_config(project_dir: Optional[str] = None) -> Config:
    """Get config instance."""
    return Config(project_dir)


