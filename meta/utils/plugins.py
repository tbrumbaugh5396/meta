"""Plugin system utilities."""

import importlib
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from meta.utils.logger import log, error


class PluginManager:
    """Manages plugins."""
    
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.plugin_dir = Path(".meta/plugins")
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
    
    def load_plugin(self, plugin_name: str, plugin_path: Optional[str] = None) -> bool:
        """Load a plugin."""
        try:
            if plugin_path:
                # Load from specific path
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[plugin_name] = module
                    spec.loader.exec_module(module)
                    
                    # Register plugin
                    if hasattr(module, "register"):
                        module.register(self)
                        self.plugins[plugin_name] = module
                        return True
        except Exception as e:
            error(f"Failed to load plugin {plugin_name}: {e}")
        
        return False
    
    def register_command(self, name: str, command: Callable, help_text: str = ""):
        """Register a plugin command."""
        # In a real implementation, this would register with Typer
        self.plugins[name] = {
            "command": command,
            "help": help_text
        }
    
    def list_plugins(self) -> List[str]:
        """List loaded plugins."""
        return list(self.plugins.keys())
    
    def get_plugin(self, name: str) -> Optional[Any]:
        """Get plugin by name."""
        return self.plugins.get(name)


def get_plugin_manager() -> PluginManager:
    """Get plugin manager instance."""
    return PluginManager()


