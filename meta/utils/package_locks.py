"""Package manager lock file generation."""

import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, error, success


def generate_npm_lock_file(component_dir: str) -> bool:
    """Generate npm package-lock.json if package.json exists."""
    comp_path = Path(component_dir)
    package_json = comp_path / "package.json"
    
    if not package_json.exists():
        return True  # No package.json, nothing to do
    
    if not shutil.which("npm"):
        error("npm is not available")
        return False
    
    log(f"Generating npm lock file for {component_dir}")
    try:
        # Run npm install to generate package-lock.json
        subprocess.run(
            ["npm", "install", "--package-lock-only"],
            cwd=component_dir,
            check=True,
            capture_output=True
        )
        success(f"npm lock file generated for {component_dir}")
        return True
    except subprocess.CalledProcessError as e:
        error(f"Failed to generate npm lock file: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return False


def generate_pip_lock_file(component_dir: str) -> bool:
    """Generate pip requirements.lock from requirements.txt."""
    comp_path = Path(component_dir)
    requirements_txt = comp_path / "requirements.txt"
    
    if not requirements_txt.exists():
        return True  # No requirements.txt, nothing to do
    
    if not shutil.which("pip") and not shutil.which("pip3"):
        error("pip is not available")
        return False
    
    pip_cmd = shutil.which("pip3") or shutil.which("pip")
    lock_file = comp_path / "requirements.lock"
    
    log(f"Generating pip lock file for {component_dir}")
    try:
        # Use pip freeze or pip-compile if available
        result = subprocess.run(
            [pip_cmd, "freeze"],
            cwd=component_dir,
            check=True,
            capture_output=True,
            text=True
        )
        
        with open(lock_file, 'w') as f:
            f.write(result.stdout)
        
        success(f"pip lock file generated: {lock_file}")
        return True
    except subprocess.CalledProcessError as e:
        error(f"Failed to generate pip lock file: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return False


def generate_cargo_lock_file(component_dir: str) -> bool:
    """Generate Cargo.lock if Cargo.toml exists."""
    comp_path = Path(component_dir)
    cargo_toml = comp_path / "Cargo.toml"
    
    if not cargo_toml.exists():
        return True  # No Cargo.toml, nothing to do
    
    if not shutil.which("cargo"):
        error("cargo is not available")
        return False
    
    log(f"Generating cargo lock file for {component_dir}")
    try:
        # Cargo generates Cargo.lock automatically
        subprocess.run(
            ["cargo", "generate-lockfile"],
            cwd=component_dir,
            check=True,
            capture_output=True
        )
        success(f"cargo lock file generated for {component_dir}")
        return True
    except subprocess.CalledProcessError as e:
        error(f"Failed to generate cargo lock file: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return False


def generate_go_lock_file(component_dir: str) -> bool:
    """Generate go.sum if go.mod exists."""
    comp_path = Path(component_dir)
    go_mod = comp_path / "go.mod"
    
    if not go_mod.exists():
        return True  # No go.mod, nothing to do
    
    if not shutil.which("go"):
        error("go is not available")
        return False
    
    log(f"Generating go lock file for {component_dir}")
    try:
        # Go generates go.sum automatically
        subprocess.run(
            ["go", "mod", "tidy"],
            cwd=component_dir,
            check=True,
            capture_output=True
        )
        success(f"go lock file generated for {component_dir}")
        return True
    except subprocess.CalledProcessError as e:
        error(f"Failed to generate go lock file: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return False


def generate_all_package_locks(component_dir: str) -> Dict[str, bool]:
    """Generate all package manager lock files for a component."""
    results = {}
    
    comp_path = Path(component_dir)
    
    # npm
    if (comp_path / "package.json").exists():
        results["npm"] = generate_npm_lock_file(component_dir)
    
    # pip
    if (comp_path / "requirements.txt").exists() or (comp_path / "setup.py").exists():
        results["pip"] = generate_pip_lock_file(component_dir)
    
    # cargo
    if (comp_path / "Cargo.toml").exists():
        results["cargo"] = generate_cargo_lock_file(component_dir)
    
    # go
    if (comp_path / "go.mod").exists():
        results["go"] = generate_go_lock_file(component_dir)
    
    return results


