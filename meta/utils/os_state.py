"""OS state management utilities."""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from meta.utils.logger import log, success, error
from meta.utils.os_config import get_os_manifest


STATE_DIR = Path(".meta/os-state")


class OSStateManager:
    """Manages OS state."""
    
    def __init__(self):
        self.state_dir = STATE_DIR
        self.state_dir.mkdir(parents=True, exist_ok=True)
    
    def capture_state(self, manifest_path: Optional[Path] = None) -> bool:
        """Capture current OS state."""
        log("Capturing OS state...")
        
        state = {
            "timestamp": datetime.now().isoformat(),
            "os": self._capture_os_info(),
            "packages": self._capture_packages(),
            "services": self._capture_services(),
            "users": self._capture_users(),
            "files": self._capture_files()
        }
        
        # Save state
        state_file = self.state_dir / f"state-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        # Update current state
        current_state_file = self.state_dir / "current.json"
        with open(current_state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        success(f"OS state captured: {state_file.name}")
        return True
    
    def _capture_os_info(self) -> Dict[str, Any]:
        """Capture OS information."""
        try:
            result = subprocess.run(
                ["uname", "-a"],
                capture_output=True,
                text=True,
                check=True
            )
            return {"uname": result.stdout.strip()}
        except:
            return {}
    
    def _capture_packages(self) -> List[Dict[str, Any]]:
        """Capture installed packages."""
        packages = []
        
        # Try dpkg (Debian/Ubuntu)
        try:
            result = subprocess.run(
                ["dpkg-query", "-W", "-f=${Package}\t${Version}\n"],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.strip().split("\n"):
                if "\t" in line:
                    name, version = line.split("\t", 1)
                    packages.append({"name": name, "version": version, "manager": "dpkg"})
        except:
            pass
        
        # Try rpm (RedHat/CentOS)
        try:
            result = subprocess.run(
                ["rpm", "-qa", "--queryformat", "%{NAME}\t%{VERSION}\n"],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.strip().split("\n"):
                if "\t" in line:
                    name, version = line.split("\t", 1)
                    packages.append({"name": name, "version": version, "manager": "rpm"})
        except:
            pass
        
        return packages
    
    def _capture_services(self) -> List[Dict[str, Any]]:
        """Capture systemd services."""
        services = []
        
        try:
            result = subprocess.run(
                ["systemctl", "list-units", "--type=service", "--no-pager", "--no-legend"],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.strip().split("\n"):
                parts = line.split()
                if parts:
                    name = parts[0]
                    active = parts[2] if len(parts) > 2 else "unknown"
                    enabled = "enabled" in line
                    services.append({
                        "name": name,
                        "active": active,
                        "enabled": enabled
                    })
        except:
            pass
        
        return services
    
    def _capture_users(self) -> List[Dict[str, Any]]:
        """Capture system users."""
        users = []
        
        try:
            result = subprocess.run(
                ["getent", "passwd"],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.strip().split("\n"):
                parts = line.split(":")
                if len(parts) >= 7:
                    users.append({
                        "username": parts[0],
                        "uid": parts[2],
                        "gid": parts[3],
                        "home": parts[5],
                        "shell": parts[6]
                    })
        except:
            pass
        
        return users
    
    def _capture_files(self) -> List[Dict[str, Any]]:
        """Capture important files (from manifest)."""
        manifest = get_os_manifest()
        files = []
        
        for file_entry in manifest.config.get("files", []):
            path = Path(file_entry.get("path"))
            if path.exists():
                try:
                    stat = path.stat()
                    files.append({
                        "path": str(path),
                        "size": stat.st_size,
                        "mode": oct(stat.st_mode)[-3:],
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except:
                    pass
        
        return files
    
    def compare_state(
        self,
        manifest_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Compare current state with manifest."""
        manifest = get_os_manifest(manifest_path)
        current_state_file = self.state_dir / "current.json"
        
        if not current_state_file.exists():
            return {"error": "No current state captured"}
        
        with open(current_state_file) as f:
            current_state = json.load(f)
        
        diff = {
            "packages": {
                "missing": [],
                "extra": [],
                "version_mismatch": []
            },
            "services": {
                "missing": [],
                "extra": [],
                "mismatch": []
            },
            "users": {
                "missing": [],
                "extra": []
            },
            "files": {
                "missing": [],
                "modified": []
            }
        }
        
        # Compare packages
        manifest_packages = {pkg.get("name"): pkg for pkg in manifest.config.get("packages", [])}
        current_packages = {pkg.get("name"): pkg for pkg in current_state.get("packages", [])}
        
        for name, pkg in manifest_packages.items():
            if name not in current_packages:
                diff["packages"]["missing"].append(name)
            else:
                desired_version = pkg.get("version")
                current_version = current_packages[name].get("version")
                if desired_version and current_version != desired_version:
                    diff["packages"]["version_mismatch"].append({
                        "name": name,
                        "desired": desired_version,
                        "current": current_version
                    })
        
        for name in current_packages:
            if name not in manifest_packages:
                diff["packages"]["extra"].append(name)
        
        # Compare services
        manifest_services = {svc.get("name"): svc for svc in manifest.config.get("services", [])}
        current_services = {svc.get("name"): svc for svc in current_state.get("services", [])}
        
        for name, svc in manifest_services.items():
            if name not in current_services:
                diff["services"]["missing"].append(name)
            else:
                desired_enabled = svc.get("enabled", True)
                current_enabled = current_services[name].get("enabled", False)
                if desired_enabled != current_enabled:
                    diff["services"]["mismatch"].append({
                        "name": name,
                        "desired_enabled": desired_enabled,
                        "current_enabled": current_enabled
                    })
        
        for name in current_services:
            if name not in manifest_services:
                diff["services"]["extra"].append(name)
        
        # Compare users
        manifest_users = {user.get("username"): user for user in manifest.config.get("users", [])}
        current_users = {user.get("username"): user for user in current_state.get("users", [])}
        
        for name in manifest_users:
            if name not in current_users:
                diff["users"]["missing"].append(name)
        
        for name in current_users:
            if name not in manifest_users:
                diff["users"]["extra"].append(name)
        
        # Compare files
        manifest_files = {f.get("path"): f for f in manifest.config.get("files", [])}
        current_files = {f.get("path"): f for f in current_state.get("files", [])}
        
        for path in manifest_files:
            if path not in current_files:
                diff["files"]["missing"].append(path)
        
        return diff
    
    def restore_state(self, state_file: Optional[Path] = None) -> bool:
        """Restore OS state from file."""
        if not state_file:
            state_file = self.state_dir / "current.json"
        
        if not state_file.exists():
            error(f"State file not found: {state_file}")
            return False
        
        log(f"Restoring OS state from {state_file.name}...")
        # In a real implementation, this would restore the state
        log("State restoration not fully implemented - use provisioning")
        return True


def get_os_state_manager() -> OSStateManager:
    """Get OS state manager."""
    return OSStateManager()


