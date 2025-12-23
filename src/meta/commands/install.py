"""Install system packages and dependencies."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, warning as warn
from meta.utils.system_packages import (
    install_system_packages_from_manifest,
    load_system_packages,
    install_python_packages,
    install_system_packages,
    detect_system_package_manager
)

app = typer.Typer(help="Install system packages and dependencies")


@app.command(name="system-packages")
def install_system_packages_cmd(
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    skip_system: bool = typer.Option(False, "--skip-system", help="Skip system package installation"),
    skip_python: bool = typer.Option(False, "--skip-python", help="Skip Python package installation"),
):
    """Install system packages from manifests/system-packages.yaml."""
    log("Installing system packages from manifest...")
    
    config = load_system_packages(manifests_dir)
    if not config:
        error("No system-packages.yaml found. Create one in manifests/ directory.")
        raise typer.Exit(code=1)
    
    all_success = True
    
    # Install system tools
    if not skip_system:
        system_tools = config.get("system_packages", {}).get("system_tools", [])
        if system_tools:
            if not install_system_packages(system_tools):
                all_success = False
        else:
            log("No system tools to install")
    
    # Install global Python packages
    if not skip_python:
        global_packages = config.get("system_packages", {}).get("global_packages", {})
        pip_packages = global_packages.get("pip", [])
        if pip_packages:
            if not install_python_packages(pip_packages, global_install=True):
                all_success = False
        else:
            log("No global Python packages to install")
    
    # Check Python version
    python_config = config.get("system_packages", {}).get("python", {})
    if python_config:
        python_version = python_config.get("version")
        if python_version:
            log(f"Python version requirement: {python_version}")
            import sys
            current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            if current_version != python_version:
                warn(f"Python version mismatch: required {python_version}, found {current_version}")
    
    if all_success:
        success("System packages installed successfully")
    else:
        error("Some system packages failed to install")
        raise typer.Exit(code=1)


@app.command(name="python")
def install_python_packages_cmd(
    packages: list[str] = typer.Argument(..., help="Python packages to install (format: package==version)"),
    global_install: bool = typer.Option(True, "--global/--local", help="Install globally or locally"),
):
    """Install Python packages."""
    if not packages:
        error("No packages specified")
        raise typer.Exit(code=1)
    
    if install_python_packages(packages, global_install=global_install):
        success(f"Python packages installed: {', '.join(packages)}")
    else:
        error("Failed to install Python packages")
        raise typer.Exit(code=1)


@app.command(name="system")
def install_system_tools_cmd(
    packages: list[str] = typer.Argument(..., help="System packages to install"),
    package_manager: Optional[str] = typer.Option(None, "--manager", "-m", help="Package manager (apt, brew, etc.)"),
):
    """Install system packages using package manager."""
    if not packages:
        error("No packages specified")
        raise typer.Exit(code=1)
    
    if install_system_packages(packages, package_manager):
        success(f"System packages installed: {', '.join(packages)}")
    else:
        error("Failed to install system packages")
        raise typer.Exit(code=1)

