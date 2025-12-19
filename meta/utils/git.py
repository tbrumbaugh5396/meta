"""Git operations for component management."""

import subprocess
import shutil
from pathlib import Path
from typing import Optional
from meta.utils.logger import log, error, success


def git_available() -> bool:
    """Check if git is available."""
    return shutil.which("git") is not None


def clone_repo(repo_url: str, target_dir: str, version: Optional[str] = None) -> bool:
    """Clone a git repository to target directory."""
    if not git_available():
        error("Git is not available")
        return False
    
    target_path = Path(target_dir)
    if target_path.exists():
        log(f"Directory {target_dir} already exists, skipping clone")
        return True
    
    log(f"Cloning {repo_url} to {target_dir}")
    try:
        subprocess.run(
            ["git", "clone", repo_url, target_dir],
            check=True,
            capture_output=True
        )
        
        if version:
            checkout_version(target_dir, version)
        
        success(f"Successfully cloned {repo_url}")
        return True
    except subprocess.CalledProcessError as e:
        error(f"Failed to clone {repo_url}: {e.stderr.decode()}")
        return False


def checkout_version(repo_dir: str, version: str) -> bool:
    """Checkout a specific version/tag in a repository."""
    if not git_available():
        error("Git is not available")
        return False
    
    log(f"Checking out version {version} in {repo_dir}")
    try:
        subprocess.run(
            ["git", "-C", repo_dir, "checkout", version],
            check=True,
            capture_output=True
        )
        success(f"Successfully checked out {version}")
        return True
    except subprocess.CalledProcessError as e:
        error(f"Failed to checkout {version}: {e.stderr.decode()}")
        return False


def pull_latest(repo_dir: str) -> bool:
    """Pull latest changes from repository."""
    if not git_available():
        error("Git is not available")
        return False
    
    log(f"Pulling latest changes in {repo_dir}")
    try:
        subprocess.run(
            ["git", "-C", repo_dir, "pull"],
            check=True,
            capture_output=True
        )
        success(f"Successfully pulled latest changes")
        return True
    except subprocess.CalledProcessError as e:
        error(f"Failed to pull latest: {e.stderr.decode()}")
        return False


def get_current_version(repo_dir: str) -> Optional[str]:
    """Get current version/tag of repository."""
    if not git_available():
        return None
    
    try:
        result = subprocess.run(
            ["git", "-C", repo_dir, "describe", "--tags", "--exact-match"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        
        # Try to get branch name
        result = subprocess.run(
            ["git", "-C", repo_dir, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        
        return None
    except Exception:
        return None


def get_commit_sha(repo_dir: str, ref: Optional[str] = None) -> Optional[str]:
    """Get the commit SHA for a repository (optionally for a specific ref)."""
    if not git_available():
        return None
    
    try:
        cmd = ["git", "-C", repo_dir, "rev-parse", "HEAD"]
        if ref:
            cmd[-1] = ref
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return None


def get_commit_sha_for_ref(repo_url: str, ref: str) -> Optional[str]:
    """Get the commit SHA for a specific ref in a remote repository without cloning."""
    if not git_available():
        return None
    
    try:
        # Use git ls-remote to get commit SHA without cloning
        result = subprocess.run(
            ["git", "ls-remote", repo_url, ref],
            capture_output=True,
            text=True,
            check=True
        )
        # Output format: "commit_sha\trefs/heads/branch" or "commit_sha\trefs/tags/tag"
        lines = result.stdout.strip().split('\n')
        if lines and lines[0]:
            return lines[0].split()[0]  # First word is the commit SHA
        return None
    except Exception:
        return None

