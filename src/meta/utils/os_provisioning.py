"""OS provisioning engine utilities."""

import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error, warning
from meta.utils.os_config import get_os_manifest


class OSProvisioningEngine:
    """OS provisioning engine."""
    
    def __init__(self):
        self.provisioners = {
            "ansible": self._provision_with_ansible,
            "terraform": self._provision_with_terraform,
            "cloud-init": self._provision_with_cloud_init,
            "shell": self._provision_with_shell
        }
    
    def provision(
        self,
        manifest_path: Optional[Path] = None,
        provider: str = "ansible",
        target: Optional[str] = None,
        dry_run: bool = False
    ) -> bool:
        """Provision OS from manifest."""
        manifest = get_os_manifest(manifest_path)
        
        # Validate manifest
        errors = manifest.validate()
        if errors:
            error("OS manifest validation failed:")
            for err in errors:
                error(f"  • {err}")
            return False
        
        log(f"Provisioning OS using {provider}...")
        
        if dry_run:
            log("DRY RUN: Would provision:")
            self._show_provision_plan(manifest)
            return True
        
        provisioner = self.provisioners.get(provider)
        if not provisioner:
            error(f"Unknown provisioning provider: {provider}")
            return False
        
        try:
            return provisioner(manifest, target)
        except Exception as e:
            error(f"Provisioning failed: {e}")
            return False
    
    def _show_provision_plan(self, manifest):
        """Show provisioning plan."""
        config = manifest.config
        
        log(f"  OS: {config.get('os', {}).get('name', 'unknown')}")
        log(f"  Packages: {len(config.get('packages', []))}")
        log(f"  Services: {len(config.get('services', []))}")
        log(f"  Users: {len(config.get('users', []))}")
        log(f"  Files: {len(config.get('files', []))}")
    
    def _provision_with_ansible(self, manifest, target: Optional[str]) -> bool:
        """Provision using Ansible."""
        log("Generating Ansible playbook...")
        
        # Generate playbook from manifest
        playbook = self._generate_ansible_playbook(manifest)
        
        # Write playbook
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(playbook)
            playbook_path = f.name
        
        try:
            # Run Ansible
            cmd = ["ansible-playbook", playbook_path]
            if target:
                cmd.extend(["-i", target])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                success("Ansible provisioning completed")
                return True
            else:
                error(f"Ansible provisioning failed: {result.stderr}")
                return False
        finally:
            Path(playbook_path).unlink()
    
    def _generate_ansible_playbook(self, manifest) -> str:
        """Generate Ansible playbook from manifest."""
        config = manifest.config
        
        playbook = "---\n- hosts: all\n  become: yes\n  tasks:\n"
        
        # Packages
        for pkg in config.get("packages", []):
            name = pkg.get("name")
            version = pkg.get("version")
            pkg_name = f"{name}={version}" if version else name
            playbook += f"    - name: Install {name}\n"
            playbook += f"      package:\n"
            playbook += f"        name: {pkg_name}\n"
            playbook += f"        state: present\n"
        
        # Services
        for svc in config.get("services", []):
            name = svc.get("name")
            enabled = svc.get("enabled", True)
            playbook += f"    - name: Manage service {name}\n"
            playbook += f"      systemd:\n"
            playbook += f"        name: {name}\n"
            playbook += f"        enabled: {enabled}\n"
            playbook += f"        state: started\n"
        
        # Users
        for user in config.get("users", []):
            username = user.get("username")
            groups = user.get("groups", [])
            home = user.get("home")
            playbook += f"    - name: Create user {username}\n"
            playbook += f"      user:\n"
            playbook += f"        name: {username}\n"
            if groups:
                playbook += f"        groups: {','.join(groups)}\n"
            if home:
                playbook += f"        home: {home}\n"
        
        # Files
        for file_entry in config.get("files", []):
            path = file_entry.get("path")
            content = file_entry.get("content")
            mode = file_entry.get("mode", "0644")
            owner = file_entry.get("owner")
            
            playbook += f"    - name: Create file {path}\n"
            playbook += f"      copy:\n"
            playbook += f"        dest: {path}\n"
            if content:
                playbook += f"        content: |\n"
                for line in content.split("\n"):
                    playbook += f"          {line}\n"
            if mode:
                playbook += f"        mode: {mode}\n"
            if owner:
                playbook += f"        owner: {owner}\n"
        
        return playbook
    
    def _provision_with_terraform(self, manifest, target: Optional[str]) -> bool:
        """Provision using Terraform."""
        log("Terraform provisioning not fully implemented")
        warning("Use Ansible or cloud-init for OS provisioning")
        return False
    
    def _provision_with_cloud_init(self, manifest, target: Optional[str]) -> bool:
        """Provision using cloud-init."""
        log("Generating cloud-init configuration...")
        
        config = manifest.config
        cloud_init = "#cloud-config\n\n"
        
        # Packages
        packages = [pkg.get("name") for pkg in config.get("packages", [])]
        if packages:
            cloud_init += "packages:\n"
            for pkg in packages:
                cloud_init += f"  - {pkg}\n"
        
        # Users
        for user in config.get("users", []):
            username = user.get("username")
            groups = user.get("groups", [])
            cloud_init += f"users:\n"
            cloud_init += f"  - name: {username}\n"
            if groups:
                cloud_init += f"    groups: {','.join(groups)}\n"
        
        # Write files
        for file_entry in config.get("files", []):
            path = file_entry.get("path")
            content = file_entry.get("content", "")
            mode = file_entry.get("mode", "0644")
            owner = file_entry.get("owner", "root")
            
            cloud_init += f"write_files:\n"
            cloud_init += f"  - path: {path}\n"
            cloud_init += f"    content: |\n"
            for line in content.split("\n"):
                cloud_init += f"      {line}\n"
            cloud_init += f"    permissions: {mode}\n"
            cloud_init += f"    owner: {owner}\n"
        
        log("Cloud-init configuration generated")
        log("Use this with cloud-init on your target system")
        print(cloud_init)
        
        return True
    
    def _provision_with_shell(self, manifest, target: Optional[str]) -> bool:
        """Provision using shell scripts."""
        log("Generating shell script...")
        
        config = manifest.config
        script = "#!/bin/bash\nset -e\n\n"
        
        # Packages
        for pkg in config.get("packages", []):
            name = pkg.get("name")
            script += f"apt-get install -y {name}\n"
        
        # Services
        for svc in config.get("services", []):
            name = svc.get("name")
            enabled = svc.get("enabled", True)
            script += f"systemctl enable {name}\n" if enabled else f"systemctl disable {name}\n"
            script += f"systemctl start {name}\n"
        
        # Users
        for user in config.get("users", []):
            username = user.get("username")
            groups = user.get("groups", [])
            script += f"useradd -m {username}\n"
            if groups:
                script += f"usermod -aG {','.join(groups)} {username}\n"
        
        # Files
        for file_entry in config.get("files", []):
            path = file_entry.get("path")
            content = file_entry.get("content", "")
            mode = file_entry.get("mode", "0644")
            owner = file_entry.get("owner", "root")
            
            script += f"cat > {path} << 'EOF'\n{content}\nEOF\n"
            script += f"chmod {mode} {path}\n"
            script += f"chown {owner} {path}\n"
        
        log("Shell script generated")
        print(script)
        
        return True


def get_provisioning_engine() -> OSProvisioningEngine:
    """Get OS provisioning engine."""
    return OSProvisioningEngine()


