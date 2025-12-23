"""Cache key computation for build artifacts."""

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log


def compute_component_cache_key(component_name: str, component_data: Dict[str, Any], 
                                dependencies: List[str], manifests_dir: str = "manifests") -> str:
    """Compute cache key for a component based on all inputs."""
    # Collect all inputs that affect the build
    inputs = {
        "component": component_name,
        "version": component_data.get("version", ""),
        "type": component_data.get("type", ""),
        "build_target": component_data.get("build_target", ""),
        "dependencies": sorted(dependencies),
        "depends_on": sorted(component_data.get("depends_on", []))
    }
    
    # Add dependency versions if available
    from meta.utils.manifest import get_components
    components = get_components(manifests_dir)
    dep_versions = {}
    for dep in dependencies:
        if dep in components:
            dep_versions[dep] = components[dep].get("version", "")
    inputs["dependency_versions"] = dep_versions
    
    # Serialize and hash
    inputs_str = json.dumps(inputs, sort_keys=True)
    cache_key = hashlib.sha256(inputs_str.encode()).hexdigest()
    
    return cache_key


def compute_build_cache_key(component_dir: str, build_target: str) -> str:
    """Compute cache key for a build based on source files and dependencies."""
    comp_path = Path(component_dir)
    
    # Collect source file hashes
    source_files = []
    for pattern in ["**/*.py", "**/*.js", "**/*.ts", "**/*.rs", "**/*.go", "**/BUILD.bazel", "**/Cargo.toml", "**/go.mod"]:
        for file_path in comp_path.glob(pattern):
            if file_path.is_file():
                try:
                    file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
                    source_files.append((str(file_path.relative_to(comp_path)), file_hash))
                except Exception:
                    pass
    
    # Sort for deterministic hashing
    source_files.sort()
    
    # Combine with build target
    inputs = {
        "build_target": build_target,
        "source_files": source_files
    }
    
    inputs_str = json.dumps(inputs, sort_keys=True)
    cache_key = hashlib.sha256(inputs_str.encode()).hexdigest()
    
    return cache_key


def get_cache_path(cache_key: str, cache_dir: str = ".meta-cache") -> Path:
    """Get the cache path for a cache key."""
    cache_path = Path(cache_dir)
    # Use first 2 chars of hash for directory structure
    cache_path = cache_path / cache_key[:2] / cache_key
    return cache_path


