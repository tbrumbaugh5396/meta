"""Package manager detection and installation utilities."""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, error, success


def detect_package_managers(component_dir: str) -> List[str]:
    """Detect which package managers are needed for a component."""
    comp_path = Path(component_dir)
    if not comp_path.exists():
        return []
    
    detected = []
    
    # Check for npm/Node.js
    if (comp_path / "package.json").exists():
        detected.append("npm")
    
    # Check for Python
    if (comp_path / "requirements.txt").exists() or (comp_path / "pyproject.toml").exists() or (comp_path / "setup.py").exists():
        detected.append("pip")
    
    # Check for Rust/Cargo
    if (comp_path / "Cargo.toml").exists():
        detected.append("cargo")
    
    # Check for Go
    if (comp_path / "go.mod").exists():
        detected.append("go")
    
    # Check for Docker
    if (comp_path / "Dockerfile").exists():
        detected.append("docker")
    
    return detected


def install_npm_dependencies(component_dir: str) -> bool:
    """Install npm dependencies for a component."""
    if not shutil.which("npm"):
        error("npm is not available")
        return False
    
    comp_path = Path(component_dir)
    package_json = comp_path / "package.json"
    
    if not package_json.exists():
        return True  # No package.json, nothing to do
    
    log(f"Installing npm dependencies for {component_dir}")
    try:
        # Use npm ci for reproducible installs (requires package-lock.json)
        lock_file = comp_path / "package-lock.json"
        if lock_file.exists():
            subprocess.run(
                ["npm", "ci"],
                cwd=component_dir,
                check=True,
                capture_output=True
            )
        else:
            # Fall back to npm install
            subprocess.run(
                ["npm", "install"],
                cwd=component_dir,
                check=True,
                capture_output=True
            )
        success(f"npm dependencies installed for {component_dir}")
        return True
    except subprocess.CalledProcessError as e:
        error(f"Failed to install npm dependencies: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return False


def install_pip_dependencies(component_dir: str) -> bool:
    """Install Python dependencies for a component."""
    if not shutil.which("pip") and not shutil.which("pip3"):
        error("pip is not available")
        return False
    
    comp_path = Path(component_dir)
    pip_cmd = shutil.which("pip3") or shutil.which("pip")
    
    # Check for requirements.txt
    requirements = comp_path / "requirements.txt"
    if requirements.exists():
        log(f"Installing pip dependencies from requirements.txt for {component_dir}")
        try:
            subprocess.run(
                [pip_cmd, "install", "-r", str(requirements)],
                cwd=component_dir,
                check=True,
                capture_output=True
            )
            success(f"pip dependencies installed for {component_dir}")
            return True
        except subprocess.CalledProcessError as e:
            error(f"Failed to install pip dependencies: {e.stderr.decode() if e.stderr else 'Unknown error'}")
            return False
    
    # Check for setup.py (install in editable mode)
    setup_py = comp_path / "setup.py"
    if setup_py.exists():
        log(f"Installing component in editable mode for {component_dir}")
        try:
            subprocess.run(
                [pip_cmd, "install", "-e", "."],
                cwd=component_dir,
                check=True,
                capture_output=True
            )
            success(f"Component installed for {component_dir}")
            return True
        except subprocess.CalledProcessError as e:
            error(f"Failed to install component: {e.stderr.decode() if e.stderr else 'Unknown error'}")
            return False
    
    return True  # No Python dependencies to install


def install_cargo_dependencies(component_dir: str) -> bool:
    """Install/build Rust dependencies for a component."""
    if not shutil.which("cargo"):
        error("cargo is not available")
        return False
    
    comp_path = Path(component_dir)
    cargo_toml = comp_path / "Cargo.toml"
    
    if not cargo_toml.exists():
        return True  # No Cargo.toml, nothing to do
    
    log(f"Building Rust dependencies for {component_dir}")
    try:
        subprocess.run(
            ["cargo", "build"],
            cwd=component_dir,
            check=True,
            capture_output=True
        )
        success(f"Rust dependencies built for {component_dir}")
        return True
    except subprocess.CalledProcessError as e:
        error(f"Failed to build Rust dependencies: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return False


def install_go_dependencies(component_dir: str) -> bool:
    """Install Go dependencies for a component."""
    if not shutil.which("go"):
        error("go is not available")
        return False
    
    comp_path = Path(component_dir)
    go_mod = comp_path / "go.mod"
    
    if not go_mod.exists():
        return True  # No go.mod, nothing to do
    
    log(f"Installing Go dependencies for {component_dir}")
    try:
        subprocess.run(
            ["go", "mod", "download"],
            cwd=component_dir,
            check=True,
            capture_output=True
        )
        success(f"Go dependencies installed for {component_dir}")
        return True
    except subprocess.CalledProcessError as e:
        error(f"Failed to install Go dependencies: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return False


def install_component_dependencies(component_dir: str, skip_packages: bool = False) -> bool:
    """Install all detected package manager dependencies for a component."""
    if skip_packages:
        return True
    
    detected = detect_package_managers(component_dir)
    
    if not detected:
        return True  # No package managers detected, nothing to do
    
    log(f"Detected package managers: {', '.join(detected)}")
    
    all_success = True
    
    for pm in detected:
        if pm == "npm":
            if not install_npm_dependencies(component_dir):
                all_success = False
        elif pm == "pip":
            if not install_pip_dependencies(component_dir):
                all_success = False
        elif pm == "cargo":
            if not install_cargo_dependencies(component_dir):
                all_success = False
        elif pm == "go":
            if not install_go_dependencies(component_dir):
                all_success = False
        # Docker is handled separately (build step)
    
    return all_success


