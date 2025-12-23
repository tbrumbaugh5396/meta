"""OS-level configuration manifest utilities."""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error


OS_MANIFEST_FILE = Path("os-manifest.yaml")


class OSManifest:
    """OS-level configuration manifest."""
    
    def __init__(self, manifest_path: Optional[Path] = None):
        self.manifest_path = manifest_path or OS_MANIFEST_FILE
        self.config = {}
        self._load()
    
    def _load(self):
        """Load OS manifest."""
        if not self.manifest_path.exists():
            self.config = self._default_config()
            return
        
        try:
            with open(self.manifest_path) as f:
                self.config = yaml.safe_load(f) or {}
        except Exception as e:
            error(f"Failed to load OS manifest: {e}")
            self.config = self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default OS configuration."""
        return {
            "os": {
                "name": "linux",
                "version": "latest",
                "distribution": "ubuntu",
                "arch": "x86_64"
            },
            "packages": [],
            "services": [],
            "users": [],
            "files": [],
            "networking": {},
            "security": {},
            "storage": {},
            "systemd": {}
        }
    
    def save(self):
        """Save OS manifest."""
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
    
    def add_package(self, name: str, version: Optional[str] = None, source: Optional[str] = None):
        """Add package to manifest."""
        if "packages" not in self.config:
            self.config["packages"] = []
        
        package = {"name": name}
        if version:
            package["version"] = version
        if source:
            package["source"] = source
        
        # Check if already exists
        existing = [p for p in self.config["packages"] if p.get("name") == name]
        if existing:
            existing[0].update(package)
        else:
            self.config["packages"].append(package)
    
    def add_service(self, name: str, enabled: bool = True, config: Optional[Dict[str, Any]] = None):
        """Add service to manifest."""
        if "services" not in self.config:
            self.config["services"] = []
        
        service = {
            "name": name,
            "enabled": enabled
        }
        if config:
            service["config"] = config
        
        # Check if already exists
        existing = [s for s in self.config["services"] if s.get("name") == name]
        if existing:
            existing[0].update(service)
        else:
            self.config["services"].append(service)
    
    def add_user(self, username: str, groups: Optional[List[str]] = None, home: Optional[str] = None):
        """Add user to manifest."""
        if "users" not in self.config:
            self.config["users"] = []
        
        user = {"username": username}
        if groups:
            user["groups"] = groups
        if home:
            user["home"] = home
        
        # Check if already exists
        existing = [u for u in self.config["users"] if u.get("username") == username]
        if existing:
            existing[0].update(user)
        else:
            self.config["users"].append(user)
    
    def add_file(
        self,
        path: str,
        content: Optional[str] = None,
        source: Optional[str] = None,
        mode: Optional[str] = None,
        owner: Optional[str] = None
    ):
        """Add file to manifest."""
        if "files" not in self.config:
            self.config["files"] = []
        
        file_entry = {"path": path}
        if content:
            file_entry["content"] = content
        if source:
            file_entry["source"] = source
        if mode:
            file_entry["mode"] = mode
        if owner:
            file_entry["owner"] = owner
        
        # Check if already exists
        existing = [f for f in self.config["files"] if f.get("path") == path]
        if existing:
            existing[0].update(file_entry)
        else:
            self.config["files"].append(file_entry)
    
    def validate(self) -> List[str]:
        """Validate OS manifest."""
        errors = []
        
        # Validate OS config
        os_config = self.config.get("os", {})
        if not os_config.get("name"):
            errors.append("OS name is required")
        
        # Validate packages
        for pkg in self.config.get("packages", []):
            if not pkg.get("name"):
                errors.append("Package name is required")
        
        # Validate services
        for svc in self.config.get("services", []):
            if not svc.get("name"):
                errors.append("Service name is required")
        
        # Validate users
        for user in self.config.get("users", []):
            if not user.get("username"):
                errors.append("User username is required")
        
        # Validate files
        for file_entry in self.config.get("files", []):
            if not file_entry.get("path"):
                errors.append("File path is required")
            if not file_entry.get("content") and not file_entry.get("source"):
                errors.append("File must have content or source")
        
        return errors


def get_os_manifest(manifest_path: Optional[Path] = None) -> OSManifest:
    """Get OS manifest instance."""
    return OSManifest(manifest_path)


