"""Component templates library utilities."""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error
from meta.utils.manifest import get_components


TEMPLATES_DIR = Path(".meta/templates")
TEMPLATES_INDEX = TEMPLATES_DIR / "index.yaml"


class TemplateLibrary:
    """Manages component templates."""
    
    def __init__(self):
        self.templates_dir = TEMPLATES_DIR
        self.index_file = TEMPLATES_INDEX
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load templates index."""
        if not self.index_file.exists():
            return {}
        
        try:
            with open(self.index_file) as f:
                return yaml.safe_load(f) or {}
        except:
            return {}
    
    def _save_index(self, index: Dict[str, Any]):
        """Save templates index."""
        with open(self.index_file, 'w') as f:
            yaml.dump(index, f, default_flow_style=False, sort_keys=False)
    
    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available templates."""
        index = self._load_index()
        templates = index.get("templates", [])
        
        if category:
            templates = [t for t in templates if t.get("category") == category]
        
        return templates
    
    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Get template by name."""
        index = self._load_index()
        templates = index.get("templates", [])
        
        for template in templates:
            if template.get("name") == name:
                return template
        
        return None
    
    def install_template(self, name: str, source: str, category: str = "general",
                        description: Optional[str] = None) -> bool:
        """Install a template."""
        template_path = self.templates_dir / name
        template_path.mkdir(parents=True, exist_ok=True)
        
        # Copy template files
        source_path = Path(source)
        if source_path.exists():
            import shutil
            if source_path.is_dir():
                shutil.copytree(source_path, template_path, dirs_exist_ok=True)
            else:
                shutil.copy2(source_path, template_path)
        else:
            error(f"Template source not found: {source}")
            return False
        
        # Update index
        index = self._load_index()
        if "templates" not in index:
            index["templates"] = []
        
        # Remove existing if present
        index["templates"] = [t for t in index["templates"] if t.get("name") != name]
        
        # Add new template
        index["templates"].append({
            "name": name,
            "category": category,
            "description": description or f"Template: {name}",
            "path": str(template_path),
            "installed_at": str(Path().cwd())
        })
        
        self._save_index(index)
        return True
    
    def publish_template(self, name: str, registry_url: Optional[str] = None) -> bool:
        """Publish template to registry."""
        template = self.get_template(name)
        if not template:
            error(f"Template {name} not found")
            return False
        
        # In a real implementation, this would upload to a registry
        log(f"Publishing template {name} to registry...")
        log("Template publishing not fully implemented - use git or file sharing")
        return True
    
    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """Search templates."""
        templates = self.list_templates()
        
        results = []
        query_lower = query.lower()
        
        for template in templates:
            name = template.get("name", "").lower()
            desc = template.get("description", "").lower()
            category = template.get("category", "").lower()
            
            if query_lower in name or query_lower in desc or query_lower in category:
                results.append(template)
        
        return results


def get_template_library() -> TemplateLibrary:
    """Get template library instance."""
    return TemplateLibrary()


