"""Content hashing for deterministic builds."""

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log


def hash_file(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        log(f"Failed to hash file {file_path}: {e}")
        return ""


def hash_directory(dir_path: Path, exclude_patterns: Optional[List[str]] = None) -> str:
    """Compute hash of directory contents."""
    if exclude_patterns is None:
        exclude_patterns = [".git", "__pycache__", "node_modules", ".meta-cache"]
    
    hashes = []
    
    for item in sorted(dir_path.rglob("*")):
        if item.is_file():
            # Check if excluded
            if any(pattern in str(item) for pattern in exclude_patterns):
                continue
            rel_path = item.relative_to(dir_path)
            file_hash = hash_file(item)
            hashes.append((str(rel_path), file_hash))
    
    # Create deterministic hash
    content = json.dumps(hashes, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()


def compute_component_content_hash(component_dir: str, 
                                   exclude_patterns: Optional[List[str]] = None) -> str:
    """Compute content hash for a component directory."""
    comp_path = Path(component_dir)
    if not comp_path.exists():
        return ""
    
    return hash_directory(comp_path, exclude_patterns)


def compute_build_inputs_hash(component_name: str, component_data: Dict[str, Any],
                              dependencies: List[str], component_dir: Optional[str] = None,
                              manifests_dir: str = "manifests") -> str:
    """Compute hash of all build inputs (source + dependencies + config)."""
    inputs = {
        "component": component_name,
        "version": component_data.get("version", ""),
        "type": component_data.get("type", ""),
        "build_target": component_data.get("build_target", ""),
        "dependencies": sorted(dependencies)
    }
    
    # Add component source hash if available
    if component_dir:
        source_hash = compute_component_content_hash(component_dir)
        inputs["source_hash"] = source_hash
    
    # Add dependency hashes
    from meta.utils.manifest import get_components
    components = get_components(manifests_dir)
    dep_hashes = {}
    for dep in dependencies:
        if dep in components:
            dep_data = components[dep]
            dep_dir = f"components/{dep}"
            if Path(dep_dir).exists():
                dep_hashes[dep] = compute_component_content_hash(dep_dir)
    inputs["dependency_hashes"] = dep_hashes
    
    # Serialize and hash
    inputs_str = json.dumps(inputs, sort_keys=True)
    return hashlib.sha256(inputs_str.encode()).hexdigest()


def compute_build_output_hash(output_path: str) -> str:
    """Compute hash of build output."""
    output = Path(output_path)
    if not output.exists():
        return ""
    
    if output.is_file():
        return hash_file(output)
    elif output.is_dir():
        return hash_directory(output)
    else:
        return ""


