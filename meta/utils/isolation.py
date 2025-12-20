"""Component isolation utilities (virtual environments, containers)."""

import subprocess
import shutil
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from meta.utils.logger import log, error, success, warning as warn


def create_venv(venv_path: Path, python_version: Optional[str] = None) -> bool:
    """Create a Python virtual environment."""
    if venv_path.exists():
        log(f"Virtual environment already exists: {venv_path}")
        return True
    
    python_cmd = "python3"
    if python_version:
        python_cmd = f"python{python_version}"
    
    # Try to find the specified Python version
    if python_version and not shutil.which(python_cmd):
        # Try alternative names
        for alt in [f"python{python_version}", f"python{python_version.replace('.', '')}", "python3"]:
            if shutil.which(alt):
                python_cmd = alt
                break
        else:
            error(f"Python {python_version} not found")
            return False
    
    log(f"Creating virtual environment at {venv_path} using {python_cmd}")
    
    try:
        subprocess.run(
            [python_cmd, "-m", "venv", str(venv_path)],
            check=True,
            capture_output=True
        )
        success(f"Virtual environment created: {venv_path}")
        return True
    except subprocess.CalledProcessError as e:
        error(f"Failed to create virtual environment: {e}")
        return False


def get_venv_python(venv_path: Path) -> Optional[Path]:
    """Get path to Python executable in virtual environment."""
    if sys.platform == "win32":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"
    
    return python_exe if python_exe.exists() else None


def get_venv_pip(venv_path: Path) -> Optional[Path]:
    """Get path to pip executable in virtual environment."""
    if sys.platform == "win32":
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:
        pip_exe = venv_path / "bin" / "pip"
    
    return pip_exe if pip_exe.exists() else None


def install_in_venv(venv_path: Path, component_dir: Path, requirements_file: Optional[str] = None) -> bool:
    """Install component dependencies in virtual environment."""
    pip_exe = get_venv_pip(venv_path)
    if not pip_exe:
        error(f"pip not found in virtual environment: {venv_path}")
        return False
    
    # Install requirements.txt if it exists
    if requirements_file:
        req_file = component_dir / requirements_file
        if req_file.exists():
            log(f"Installing requirements from {req_file} in venv")
            try:
                subprocess.run(
                    [str(pip_exe), "install", "-r", str(req_file)],
                    check=True,
                    capture_output=True
                )
                success(f"Requirements installed in venv")
                return True
            except subprocess.CalledProcessError as e:
                error(f"Failed to install requirements in venv: {e}")
                return False
    
    # Install component in editable mode if setup.py exists
    setup_py = component_dir / "setup.py"
    if setup_py.exists():
        log(f"Installing component in editable mode in venv")
        try:
            subprocess.run(
                [str(pip_exe), "install", "-e", str(component_dir)],
                check=True,
                capture_output=True
            )
            success(f"Component installed in venv")
            return True
        except subprocess.CalledProcessError as e:
            error(f"Failed to install component in venv: {e}")
            return False
    
    return True


def get_component_venv_path(component_name: str, base_dir: Path = Path(".meta/venvs")) -> Path:
    """Get path to component's virtual environment."""
    return base_dir / component_name


def setup_component_isolation(component_name: str, component_dir: Path, 
                              isolation_config: Dict[str, Any]) -> Optional[Path]:
    """Set up isolation for a component (venv, docker, etc.)."""
    isolation_type = isolation_config.get("type", "none")
    
    if isolation_type == "none" or not isolation_type:
        return None
    
    if isolation_type == "venv":
        venv_path = get_component_venv_path(component_name)
        python_version = isolation_config.get("python_version")
        
        if not create_venv(venv_path, python_version):
            return None
        
        # Install dependencies in venv
        requirements = isolation_config.get("requirements", "requirements.txt")
        if not install_in_venv(venv_path, component_dir, requirements):
            warn(f"Failed to install dependencies in venv for {component_name}")
        
        return venv_path
    
    elif isolation_type == "docker":
        # Docker support
        from pathlib import Path
        dockerfile_path = component_dir / "Dockerfile"
        if not dockerfile_path.exists():
            warn(f"Dockerfile not found for {component_name}, skipping Docker isolation")
            return None
        
        log(f"Building Docker container for {component_name}")
        try:
            import subprocess
            image_name = f"{component_name}:latest"
            subprocess.run(
                ["docker", "build", "-t", image_name, str(component_dir)],
                check=True,
                capture_output=True
            )
            success(f"Docker container built: {image_name}")
            return Path(f".meta/containers/{component_name}")  # Return container path
        except subprocess.CalledProcessError as e:
            error(f"Failed to build Docker container: {e}")
            return None
        except FileNotFoundError:
            error("Docker not found. Install Docker to use container isolation.")
            return None
    
    else:
        warn(f"Unknown isolation type: {isolation_type}")
        return None


def run_in_venv(venv_path: Path, command: List[str], cwd: Optional[Path] = None) -> bool:
    """Run a command in a virtual environment."""
    python_exe = get_venv_python(venv_path)
    if not python_exe:
        error(f"Python not found in venv: {venv_path}")
        return False
    
    # On Unix, we can activate the venv and run the command
    # On Windows, we use the python executable directly
    if sys.platform == "win32":
        full_cmd = [str(python_exe)] + command
    else:
        # Use the venv's python directly
        full_cmd = [str(python_exe)] + command
    
    try:
        subprocess.run(
            full_cmd,
            cwd=cwd,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        error(f"Command failed in venv: {e}")
        return False

