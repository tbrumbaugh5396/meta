"""OS deployment utilities."""

import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error
from meta.utils.os_config import get_os_manifest


class OSDeployment:
    """OS deployment manager."""
    
    def deploy(
        self,
        manifest_path: Optional[Path] = None,
        target: str = "local",
        method: str = "provision"
    ) -> bool:
        """Deploy OS configuration."""
        manifest = get_os_manifest(manifest_path)
        
        log(f"Deploying OS configuration to {target} using {method}...")
        
        if method == "provision":
            return self._deploy_provision(manifest, target)
        elif method == "image":
            return self._deploy_image(manifest, target)
        elif method == "container":
            return self._deploy_container(manifest, target)
        else:
            error(f"Unknown deployment method: {method}")
            return False
    
    def _deploy_provision(self, manifest, target: str) -> bool:
        """Deploy via provisioning."""
        from meta.utils.os_provisioning import get_provisioning_engine
        
        engine = get_provisioning_engine()
        return engine.provision(manifest.manifest_path, provider="ansible", target=target)
    
    def _deploy_image(self, manifest, target: str) -> bool:
        """Deploy via OS image."""
        from meta.utils.os_build import get_os_build_system
        
        build_system = get_os_build_system()
        
        # Build image
        if not build_system.build_image(manifest.manifest_path, format="docker"):
            return False
        
        # Deploy image
        log(f"Deploying image to {target}...")
        # In a real implementation, push to registry or copy to target
        success("Image deployment not fully implemented")
        return True
    
    def _deploy_container(self, manifest, target: str) -> bool:
        """Deploy via container."""
        from meta.utils.os_build import get_os_build_system
        
        build_system = get_os_build_system()
        
        # Build container image
        image_name = f"os-{target}:latest"
        if not build_system.build_image(manifest.manifest_path, output=image_name, format="docker"):
            return False
        
        # Run container
        log(f"Running container on {target}...")
        try:
            result = subprocess.run(
                ["docker", "run", "-d", "--name", f"os-{target}", image_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                success(f"Container deployed: os-{target}")
                return True
            else:
                error(f"Container deployment failed: {result.stderr}")
                return False
        except FileNotFoundError:
            error("Docker not found. Install Docker to deploy containers.")
            return False


def get_os_deployment() -> OSDeployment:
    """Get OS deployment manager."""
    return OSDeployment()


