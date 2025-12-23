"""Component registry utilities."""

import json
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error


class ComponentRegistry:
    """Component registry client."""
    
    def __init__(self, registry_url: str = "https://registry.meta-repo.io"):
        self.registry_url = registry_url
        self.cache_file = Path(".meta/registry_cache.json")
        self.cache: Dict[str, Any] = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load registry cache."""
        if not self.cache_file.exists():
            return {}
        
        try:
            with open(self.cache_file) as f:
                return json.load(f)
        except:
            return {}
    
    def _save_cache(self):
        """Save registry cache."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for components."""
        try:
            response = requests.get(
                f"{self.registry_url}/api/v1/components/search",
                params={"q": query},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get("components", [])
        except Exception as e:
            error(f"Failed to search registry: {e}")
            # Fallback to cache
            return self._search_cache(query)
        
        return []
    
    def _search_cache(self, query: str) -> List[Dict[str, Any]]:
        """Search in cache."""
        results = []
        for comp_name, comp_data in self.cache.get("components", {}).items():
            if query.lower() in comp_name.lower():
                results.append(comp_data)
        return results
    
    def get_component(self, name: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get component information."""
        try:
            url = f"{self.registry_url}/api/v1/components/{name}"
            if version:
                url += f"/{version}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            error(f"Failed to get component: {e}")
        
        return None
    
    def publish(self, component_name: str, metadata: Dict[str, Any]) -> bool:
        """Publish component to registry."""
        try:
            response = requests.post(
                f"{self.registry_url}/api/v1/components",
                json={
                    "name": component_name,
                    **metadata
                },
                timeout=30
            )
            
            return response.status_code in [200, 201]
        except Exception as e:
            error(f"Failed to publish component: {e}")
            return False
    
    def install(self, component_name: str, version: Optional[str] = None,
               target_dir: str = "components") -> bool:
        """Install component from registry."""
        comp_info = self.get_component(component_name, version)
        
        if not comp_info:
            error(f"Component {component_name} not found in registry")
            return False
        
        repo_url = comp_info.get("repo")
        if not repo_url:
            error(f"No repository URL for {component_name}")
            return False
        
        # Clone repository
        from meta.utils.git import clone_repo
        target_path = f"{target_dir}/{component_name}"
        
        if clone_repo(repo_url, target_path, version or "latest"):
            success(f"Installed {component_name} from registry")
            return True
        else:
            error(f"Failed to install {component_name}")
            return False


def get_registry(registry_url: Optional[str] = None) -> ComponentRegistry:
    """Get registry instance."""
    return ComponentRegistry(registry_url or "https://registry.meta-repo.io")


