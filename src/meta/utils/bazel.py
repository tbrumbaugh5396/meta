"""Bazel integration for builds and tests."""

import subprocess
import shutil
from pathlib import Path
from typing import List, Optional
from meta.utils.logger import log, error, success


def bazel_available() -> bool:
    """Check if Bazel is available."""
    return shutil.which("bazel") is not None


def run_bazel_command(
    command: str,
    target: str,
    workspace_dir: Optional[str] = None,
    extra_args: Optional[List[str]] = None
) -> bool:
    """Run a Bazel command."""
    if not bazel_available():
        error("Bazel is not available")
        return False
    
    cmd = ["bazel", command, target]
    if extra_args:
        cmd.extend(extra_args)
    
    if workspace_dir:
        cwd = Path(workspace_dir)
    else:
        cwd = None
    
    log(f"Running: bazel {command} {target}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        success(f"Bazel {command} succeeded for {target}")
        return True
    except subprocess.CalledProcessError as e:
        error(f"Bazel {command} failed for {target}")
        if e.stdout:
            log(f"stdout: {e.stdout}")
        if e.stderr:
            error(f"stderr: {e.stderr}")
        return False


def run_bazel_build(target: str, workspace_dir: Optional[str] = None) -> bool:
    """Build a Bazel target."""
    return run_bazel_command("build", target, workspace_dir)


def run_bazel_test(target: str, workspace_dir: Optional[str] = None) -> bool:
    """Test a Bazel target."""
    return run_bazel_command("test", target, workspace_dir, ["--test_output=errors"])


def run_bazel_query(query: str, workspace_dir: Optional[str] = None) -> Optional[str]:
    """Run a Bazel query and return output."""
    if not bazel_available():
        error("Bazel is not available")
        return None
    
    cmd = ["bazel", "query", query]
    
    if workspace_dir:
        cwd = Path(workspace_dir)
    else:
        cwd = None
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error(f"Bazel query failed: {e.stderr}")
        return None


def check_bazel_target_exists(target: str, workspace_dir: Optional[str] = None) -> bool:
    """Check if a Bazel target exists."""
    query_result = run_bazel_query(target, workspace_dir)
    return query_result is not None and target in query_result


