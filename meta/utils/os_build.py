"""OS build system utilities."""

import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error
from meta.utils.os_config import get_os_manifest


class OSBuildSystem:
    """OS build system."""
    
    def build_image(
        self,
        manifest_path: Optional[Path] = None,
        output: Optional[str] = None,
        format: str = "docker"
    ) -> bool:
        """Build OS image from manifest."""
        manifest = get_os_manifest(manifest_path)
        
        log(f"Building OS image in {format} format...")
        
        if format == "docker":
            return self._build_docker_image(manifest, output)
        elif format == "iso":
            return self._build_iso_image(manifest, output)
        elif format == "qcow2":
            return self._build_qcow2_image(manifest, output)
        else:
            error(f"Unsupported image format: {format}")
            return False
    
    def _build_docker_image(self, manifest, output: Optional[str]) -> bool:
        """Build Docker image."""
        log("Generating Dockerfile...")
        
        config = manifest.config
        os_config = config.get("os", {})
        distro = os_config.get("distribution", "ubuntu")
        version = os_config.get("version", "latest")
        
        dockerfile = f"FROM {distro}:{version}\n\n"
        dockerfile += "RUN apt-get update && apt-get install -y \\\n"
        
        # Packages
        packages = [pkg.get("name") for pkg in config.get("packages", [])]
        if packages:
            dockerfile += "    " + " \\\n    ".join(packages) + "\n"
        
        dockerfile += "\n"
        
        # Files
        for file_entry in config.get("files", []):
            path = file_entry.get("path")
            content = file_entry.get("content", "")
            mode = file_entry.get("mode", "0644")
            owner = file_entry.get("owner", "root")
            
            dockerfile += f"RUN mkdir -p {Path(path).parent}\n"
            dockerfile += f"RUN echo '{content}' > {path}\n"
            dockerfile += f"RUN chmod {mode} {path}\n"
            dockerfile += f"RUN chown {owner} {path}\n\n"
        
        # Services
        for svc in config.get("services", []):
            name = svc.get("name")
            enabled = svc.get("enabled", True)
            if enabled:
                dockerfile += f"RUN systemctl enable {name}\n"
        
        dockerfile += "\nCMD [\"/bin/bash\"]\n"
        
        # Write Dockerfile
        dockerfile_path = Path("Dockerfile")
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile)
        
        # Build image
        image_name = output or "os-image:latest"
        log(f"Building Docker image: {image_name}")
        
        try:
            result = subprocess.run(
                ["docker", "build", "-t", image_name, "."],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                success(f"Docker image built: {image_name}")
                return True
            else:
                error(f"Docker build failed: {result.stderr}")
                return False
        except FileNotFoundError:
            error("Docker not found. Install Docker to build images.")
            return False
    
    def _build_iso_image(self, manifest, output: Optional[str]) -> bool:
        """Build ISO image."""
        log("ISO image building not fully implemented")
        log("Use tools like debian-installer or custom ISO builders")
        return False
    
    def _build_qcow2_image(self, manifest, output: Optional[str]) -> bool:
        """Build QCOW2 image."""
        log("QCOW2 image building not fully implemented")
        log("Use tools like virt-builder or packer")
        return False


def get_os_build_system() -> OSBuildSystem:
    """Get OS build system."""
    return OSBuildSystem()


