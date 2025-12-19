"""Manifest loading and validation."""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from meta.utils.logger import error


def find_meta_repo_root(start_path: Optional[str] = None) -> Optional[Path]:
    """Find the meta-repo root by looking for manifests/ directory."""
    if start_path is None:
        start_path = os.getcwd()
    
    current = Path(start_path).resolve()
    
    # Walk up the directory tree
    for path in [current] + list(current.parents):
        manifests_dir = path / "manifests"
        if manifests_dir.exists() and manifests_dir.is_dir():
            # Verify it's a meta-repo by checking for components.yaml
            if (manifests_dir / "components.yaml").exists():
                return path
    
    return None


def load_yaml(file_path: str) -> Dict[str, Any]:
    """Load and parse a YAML file."""
    path = Path(file_path)
    if not path.exists():
        error(f"Manifest file not found: {file_path}")
        raise FileNotFoundError(f"Manifest file not found: {file_path}")
    
    with open(path, 'r') as f:
        try:
            return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            error(f"Failed to parse YAML file {file_path}: {e}")
            raise


def get_components(manifests_dir: str = "manifests") -> Dict[str, Any]:
    """Load components manifest."""
    return load_yaml(f"{manifests_dir}/components.yaml").get("components", {})


def get_features(manifests_dir: str = "manifests") -> Dict[str, Any]:
    """Load features manifest."""
    return load_yaml(f"{manifests_dir}/features.yaml").get("features", {})


def get_environments(manifests_dir: str = "manifests") -> Dict[str, Any]:
    """Load environments manifest."""
    return load_yaml(f"{manifests_dir}/environments.yaml").get("environments", {})


def get_environment_config(env: str, manifests_dir: str = "manifests") -> Dict[str, Any]:
    """Get configuration for a specific environment."""
    environments = get_environments(manifests_dir)
    return environments.get(env, {})


