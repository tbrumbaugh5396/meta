"""System package management utilities."""

import subprocess
import shutil
import platform
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, error, success, warning as warn
from meta.utils.manifest import find_meta_repo_root


def get_system_packages_path(manifests_dir: str = "manifests") -> Optional[Path]:
    """Get path to system-packages.yaml manifest."""
    root = find_meta_repo_root()
    if not root:
        return None
    
    path = root / manifests_dir / "system-packages.yaml"
    return path if path.exists() else None


def load_system_packages(manifests_dir: str = "manifests") -> Dict[str, Any]:
    """Load system packages manifest."""
    path = get_system_packages_path(manifests_dir)
    if not path:
        return {}
    
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        error(f"Failed to load system-packages.yaml: {e}")
        return {}


def detect_system_package_manager() -> Optional[str]:
    """Detect system package manager (apt, brew, yum, etc.)."""
    system = platform.system().lower()
    
    if system == "linux":
        if shutil.which("apt"):
            return "apt"
        elif shutil.which("yum"):
            return "yum"
        elif shutil.which("dnf"):
            return "dnf"
        elif shutil.which("pacman"):
            return "pacman"
    elif system == "darwin":  # macOS
        if shutil.which("brew"):
            return "brew"
    elif system == "windows":
        if shutil.which("choco"):
            return "choco"
        elif shutil.which("winget"):
            return "winget"
    
    return None


def install_system_packages(packages: List[str], package_manager: Optional[str] = None) -> bool:
    """Install system packages using detected package manager."""
    if not package_manager:
        package_manager = detect_system_package_manager()
    
    if not package_manager:
        warn("No system package manager detected. Skipping system package installation.")
        return True  # Not an error, just skip
    
    if not packages:
        return True
    
    log(f"Installing system packages using {package_manager}: {', '.join(packages)}")
    
    try:
        if package_manager == "apt":
            subprocess.run(
                ["sudo", "apt", "update"],
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["sudo", "apt", "install", "-y"] + packages,
                check=True,
                capture_output=True
            )
        elif package_manager == "brew":
            subprocess.run(
                ["brew", "install"] + packages,
                check=True,
                capture_output=True
            )
        elif package_manager == "yum":
            subprocess.run(
                ["sudo", "yum", "install", "-y"] + packages,
                check=True,
                capture_output=True
            )
        elif package_manager == "dnf":
            subprocess.run(
                ["sudo", "dnf", "install", "-y"] + packages,
                check=True,
                capture_output=True
            )
        elif package_manager == "pacman":
            subprocess.run(
                ["sudo", "pacman", "-S", "--noconfirm"] + packages,
                check=True,
                capture_output=True
            )
        elif package_manager == "choco":
            subprocess.run(
                ["choco", "install", "-y"] + packages,
                check=True,
                capture_output=True
            )
        elif package_manager == "winget":
            for pkg in packages:
                subprocess.run(
                    ["winget", "install", pkg],
                    check=True,
                    capture_output=True
                )
        else:
            warn(f"Unsupported package manager: {package_manager}")
            return False
        
        success(f"System packages installed: {', '.join(packages)}")
        return True
    except subprocess.CalledProcessError as e:
        error(f"Failed to install system packages: {e}")
        return False


def install_python_packages(packages: List[str], global_install: bool = True, venv_path: Optional[str] = None) -> bool:
    """Install Python packages globally or in a virtual environment."""
    pip_cmd = shutil.which("pip3") or shutil.which("pip")
    if not pip_cmd:
        error("pip is not available")
        return False
    
    if not packages:
        return True
    
    # Format packages with versions if specified
    formatted_packages = []
    for pkg in packages:
        if isinstance(pkg, dict):
            name = pkg.get("name", "")
            version = pkg.get("version", "")
            if version:
                formatted_packages.append(f"{name}=={version}")
            else:
                formatted_packages.append(name)
        else:
            formatted_packages.append(str(pkg))
    
    cmd = [pip_cmd, "install"] + formatted_packages
    
    if venv_path:
        # Use venv's pip
        venv_pip = Path(venv_path) / "bin" / "pip"
        if not venv_pip.exists():
            venv_pip = Path(venv_path) / "Scripts" / "pip.exe"
        if venv_pip.exists():
            cmd = [str(venv_pip)] + cmd[1:]
    
    log(f"Installing Python packages: {', '.join(formatted_packages)}")
    
    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True
        )
        success(f"Python packages installed: {', '.join(formatted_packages)}")
        return True
    except subprocess.CalledProcessError as e:
        error(f"Failed to install Python packages: {e}")
        return False


def install_system_packages_from_manifest(manifests_dir: str = "manifests", skip_system: bool = False) -> bool:
    """Install all system packages from manifest."""
    config = load_system_packages(manifests_dir)
    if not config:
        log("No system-packages.yaml found, skipping system package installation")
        return True
    
    all_success = True
    
    # Install system tools
    if not skip_system:
        system_tools = config.get("system_packages", {}).get("system_tools", [])
        if system_tools:
            if not install_system_packages(system_tools):
                all_success = False
    
    # Install global Python packages
    global_packages = config.get("system_packages", {}).get("global_packages", {})
    pip_packages = global_packages.get("pip", [])
    if pip_packages:
        if not install_python_packages(pip_packages, global_install=True):
            all_success = False
    
    # Check Python version requirement
    python_version = config.get("system_packages", {}).get("python", {}).get("version")
    if python_version:
        log(f"Python version requirement: {python_version}")
        # Verify Python version (informational only)
        import sys
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        if current_version != python_version:
            warn(f"Python version mismatch: required {python_version}, found {current_version}")
    
    return all_success

