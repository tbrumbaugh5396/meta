"""Git operations for meta-repo and components."""

import typer
import subprocess
import os
from pathlib import Path
from typing import Optional, List
from meta.utils.logger import log, success, error
from meta.utils.manifest import get_components, find_meta_repo_root
from meta.utils.git import git_available

app = typer.Typer(help="Git operations for meta-repo and components")


def run_git_command(
    git_args: List[str],
    repo_dir: Optional[Path] = None,
    show_output: bool = True
):
    """Run a git command and return success status, stdout, and stderr."""
    if not git_available():
        error("Git is not available")
        return False, None, "Git is not available"
    
    cmd = ["git"] + git_args
    
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=False
        )
        
        if show_output and result.stdout:
            print(result.stdout, end="")
        if show_output and result.stderr and result.returncode != 0:
            print(result.stderr, end="", file=__import__("sys").stderr)
        
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        error(f"Failed to run git command: {e}")
        return False, None, str(e)


def get_meta_repo_root() -> Optional[Path]:
    """Get the meta-repo root directory."""
    root = find_meta_repo_root()
    if root:
        return root
    # Fallback: try current directory
    if (Path.cwd() / "manifests" / "components.yaml").exists():
        return Path.cwd()
    return None


def execute_git_command(
    git_args: List[str],
    component: Optional[str] = None,
    all_components: bool = False,
    meta_repo: bool = False,
    manifests_dir: str = "manifests",
):
    """Execute a git command on the specified target(s)."""
    # Extract actual values if OptionInfo objects were passed (shouldn't happen, but handle it)
    import typer.models
    if isinstance(component, typer.models.OptionInfo):
        component = None
    if isinstance(all_components, typer.models.OptionInfo):
        all_components = False
    if isinstance(meta_repo, typer.models.OptionInfo):
        meta_repo = False
    if isinstance(manifests_dir, typer.models.OptionInfo):
        manifests_dir = "manifests"
    
    # Final safety filter: remove any meta-repo flags from git_args
    meta_repo_flags = ("--meta-repo", "--component", "-c", "--all", "-a", "--manifests", "--parallel", "-p")
    filtered_git_args = []
    skip_next = False
    for arg in git_args:
        if skip_next:
            skip_next = False
            continue
        if arg in meta_repo_flags:
            if arg in ("--component", "-c", "--manifests"):
                skip_next = True  # Skip the next argument (the value)
            continue
        filtered_git_args.append(arg)
    git_args = filtered_git_args
    
    # Determine target(s)
    if meta_repo:
        # Run on meta-repo root
        root = get_meta_repo_root()
        if not root:
            error("Could not find meta-repo root. Run from meta-repo directory or use --manifests to specify.")
            raise typer.Exit(code=1)
        
        log(f"Running git {' '.join(git_args)} in meta-repo root")
        success_flag, _, _ = run_git_command(git_args, repo_dir=root)
        if not success_flag:
            raise typer.Exit(code=1)
        return
    
    elif component:
        # Run on specific component
        comp_dir = Path(f"components/{component}")
        if not comp_dir.exists():
            error(f"Component {component} not found at {comp_dir}")
            error(f"Run 'meta apply --component {component}' to check it out first.")
            raise typer.Exit(code=1)
        
        log(f"Running git {' '.join(git_args)} in {component}")
        success_flag, _, _ = run_git_command(git_args, repo_dir=comp_dir)
        if not success_flag:
            raise typer.Exit(code=1)
        return
    
    elif all_components:
        # Run on all components
        components = get_components(manifests_dir)
        if not components:
            error("No components found in manifest")
            raise typer.Exit(code=1)
        
        results = []
        for comp_name in components.keys():
            comp_dir = Path(f"components/{comp_name}")
            if not comp_dir.exists():
                log(f"Skipping {comp_name} (not checked out)")
                results.append({"component": comp_name, "success": False, "skipped": True})
                continue
            
            log(f"Running git {' '.join(git_args)} in {comp_name}")
            success_flag, _, _ = run_git_command(git_args, repo_dir=comp_dir)
            results.append({"component": comp_name, "success": success_flag, "skipped": False})
        
        successful = sum(1 for r in results if r.get("success"))
        total = len([r for r in results if not r.get("skipped")])
        
        if total == 0:
            error("No components are checked out. Run 'meta apply --all' to check out all components.")
            raise typer.Exit(code=1)
        
        if successful == total:
            success(f"Git command succeeded in {successful}/{total} component(s)")
        else:
            error(f"Git command failed in {total - successful}/{total} component(s)")
            raise typer.Exit(code=1)
        return
    
    else:
        # Default: run on meta-repo root if no target specified
        root = get_meta_repo_root()
        if not root:
            error("Could not find meta-repo root. Specify --meta-repo, --component, or --all")
            raise typer.Exit(code=1)
        
        log(f"Running git {' '.join(git_args)} in meta-repo root")
        success_flag, _, _ = run_git_command(git_args, repo_dir=root)
        if not success_flag:
            raise typer.Exit(code=1)


@app.callback(invoke_without_command=True)
def git(
    ctx: typer.Context,
    git_args: List[str] = typer.Argument(..., help="Git command and arguments"),
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Run on specific component"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Run on all components"),
    meta_repo: bool = typer.Option(False, "--meta-repo", help="Run on meta-repo root"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
    parallel: bool = typer.Option(False, "--parallel", "-p", help="Execute in parallel (not yet implemented)"),
):
    """Run git commands on meta-repo or components.
    
    Examples:
        # Run on meta-repo root
        meta git status --meta-repo
        meta git add . --meta-repo
        meta git commit -m "Update" --meta-repo
        
        # Run on specific component
        meta git status --component agent-core
        meta git pull --component agent-core
        
        # Run on all components
        meta git status --all
        meta git pull --all
    """
    if ctx.invoked_subcommand is not None:
        return
    
    if not git_args:
        error("Git command is required")
        raise typer.Exit(code=1)
    
    # Filter out meta-repo specific flags from git_args
    filtered_git_args = []
    skip_next = False
    for i, arg in enumerate(git_args):
        if skip_next:
            skip_next = False
            continue
        # Skip meta-repo flags
        if arg in ("--meta-repo", "--component", "-c", "--all", "-a", "--manifests", "--parallel", "-p"):
            if arg in ("--component", "-c", "--manifests"):
                skip_next = True  # Skip the next argument (the value)
            continue
        filtered_git_args.append(arg)
    
    execute_git_command(filtered_git_args, component, all_components, meta_repo, manifests_dir)


# Convenience subcommands for common git operations
@app.command()
def status(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Check status of specific component"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Check status of all components"),
    meta_repo: bool = typer.Option(False, "--meta-repo", help="Check status of meta-repo root"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Show git status."""
    execute_git_command(["status"], component, all_components, meta_repo, manifests_dir)


@app.command()
def add(
    files: List[str] = typer.Argument(..., help="Files to add"),
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Add files in specific component"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Add files in all components"),
    meta_repo: bool = typer.Option(False, "--meta-repo", help="Add files in meta-repo root"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Add files to git staging."""
    git_args = ["add"] + files
    execute_git_command(git_args, component, all_components, meta_repo, manifests_dir)


@app.command()
def commit(
    message: str = typer.Option(..., "--message", "-m", help="Commit message"),
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Commit in specific component"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Commit in all components"),
    meta_repo: bool = typer.Option(False, "--meta-repo", help="Commit in meta-repo root"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Create a git commit."""
    git_args = ["commit", "-m", message]
    execute_git_command(git_args, component, all_components, meta_repo, manifests_dir)


@app.command()
def push(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Push specific component"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Push all components"),
    meta_repo: bool = typer.Option(False, "--meta-repo", help="Push meta-repo root"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
    remote: Optional[str] = typer.Option(None, "--remote", "-r", help="Remote name"),
    branch: Optional[str] = typer.Option(None, "--branch", "-b", help="Branch name"),
):
    """Push changes to remote."""
    git_args = ["push"]
    if remote and branch:
        git_args.extend([remote, branch])
    elif remote:
        git_args.append(remote)
    
    execute_git_command(git_args, component, all_components, meta_repo, manifests_dir)


@app.command()
def pull(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Pull specific component"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Pull all components"),
    meta_repo: bool = typer.Option(False, "--meta-repo", help="Pull meta-repo root"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Pull latest changes from remote."""
    execute_git_command(["pull"], component, all_components, meta_repo, manifests_dir)


@app.command(name="log")
def git_log_cmd(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Show log for specific component"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Show log for all components"),
    meta_repo: bool = typer.Option(False, "--meta-repo", help="Show log for meta-repo root"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
    git_log_args: List[str] = typer.Argument(None, help="Git log arguments (e.g., --oneline, -n, 10)"),
):
    """Show git log. Pass git log options as arguments.
    
    Examples:
        meta git log --oneline -n 10 --meta-repo
        meta git log --graph --all --meta-repo
    """
    git_args = ["log"]
    if git_log_args:
        # Filter out any meta-repo flags that might have been passed as arguments
        filtered_args = [arg for arg in git_log_args if arg not in ("--meta-repo", "--component", "-c", "--all", "-a", "--manifests", "--parallel", "-p")]
        git_args.extend(filtered_args)
    
    execute_git_command(git_args, component, all_components, meta_repo, manifests_dir)


@app.command()
def diff(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Show diff for specific component"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Show diff for all components"),
    meta_repo: bool = typer.Option(False, "--meta-repo", help="Show diff for meta-repo root"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Show git diff."""
    execute_git_command(["diff"], component, all_components, meta_repo, manifests_dir)


@app.command()
def branch(
    branch_name: Optional[str] = typer.Argument(None, help="Branch name (optional)"),
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Branch operation for specific component"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Branch operation for all components"),
    meta_repo: bool = typer.Option(False, "--meta-repo", help="Branch operation for meta-repo root"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
    create: bool = typer.Option(False, "--create", "-b", help="Create new branch"),
    delete: bool = typer.Option(False, "--delete", "-d", help="Delete branch"),
    list_branches: bool = typer.Option(False, "--list", help="List branches"),
):
    """Manage git branches."""
    git_args = ["branch"]
    if create and branch_name:
        git_args.extend(["-b", branch_name])
    elif delete and branch_name:
        git_args.extend(["-d", branch_name])
    elif list_branches:
        git_args.append("-a")  # List all branches
    elif branch_name:
        git_args.append(branch_name)
    
    execute_git_command(git_args, component, all_components, meta_repo, manifests_dir)


@app.command()
def checkout(
    ref: str = typer.Argument(..., help="Branch, tag, or commit to checkout"),
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Checkout in specific component"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Checkout in all components"),
    meta_repo: bool = typer.Option(False, "--meta-repo", help="Checkout in meta-repo root"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Checkout a branch, tag, or commit."""
    execute_git_command(["checkout", ref], component, all_components, meta_repo, manifests_dir)

