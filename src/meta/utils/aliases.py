"""Component alias utilities."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from meta.utils.logger import log, success, error
from meta.utils.manifest import get_components


ALIASES_FILE = Path(".meta/aliases.yaml")


def load_aliases() -> Dict[str, str]:
    """Load aliases."""
    if not ALIASES_FILE.exists():
        return {}
    
    try:
        with open(ALIASES_FILE) as f:
            data = yaml.safe_load(f) or {}
            return data.get("aliases", {})
    except:
        return {}


def save_aliases(aliases: Dict[str, str]):
    """Save aliases."""
    ALIASES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ALIASES_FILE, 'w') as f:
        yaml.dump({"aliases": aliases}, f, default_flow_style=False, sort_keys=False)


def create_alias(alias_type: str, alias: str, target: str) -> bool:
    """Create an alias."""
    aliases = load_aliases()
    
    key = f"{alias_type}:{alias}"
    aliases[key] = target
    
    save_aliases(aliases)
    return True


def delete_alias(alias_type: str, alias: str) -> bool:
    """Delete an alias."""
    aliases = load_aliases()
    
    key = f"{alias_type}:{alias}"
    if key in aliases:
        del aliases[key]
        save_aliases(aliases)
        return True
    
    return False


def resolve_alias(alias_type: str, alias: str) -> Optional[str]:
    """Resolve an alias."""
    aliases = load_aliases()
    key = f"{alias_type}:{alias}"
    return aliases.get(key)


def list_aliases(alias_type: Optional[str] = None) -> Dict[str, str]:
    """List aliases."""
    aliases = load_aliases()
    
    if alias_type:
        filtered = {}
        for key, value in aliases.items():
            if key.startswith(f"{alias_type}:"):
                filtered[key.split(":", 1)[1]] = value
        return filtered
    
    return aliases


