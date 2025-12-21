"""Update all repositories (git add, commit, push)."""

import typer
import subprocess
from pathlib import Path
from typing import Optional, List
from meta.utils.logger import log, success, error, warning
from meta.utils.manifest import get_components, find_meta_repo_root

app = typer.Typer(help="Update all repositories with git operations")


def is_git_repo(path: Path) -> bool:
    """Check if a directory is a git repository."""
    return (path / ".git").exists() or (path / ".git").is_file()


def get_sibling_repos(meta_repo_root: Path) -> List[Path]:
    """Get all sibling directories that are git repositories."""
    parent = meta_repo_root.parent
    repos = []
    
    # Known meta-repos
    meta_repo_names = ["meta-repo", "gambling-platform-meta", "scraping-platform-meta", "platform-meta"]
    
    # Known component repos
    component_names = [
        "agent-core", "detector-core", "ai-coding-learner", "infrastructure-primitives",
        "integrations", "betting-calculators", "social-platform", "live-betting-engine",
        "fund-transfer-engine", "data-processing"
    ]
    
    all_repo_names = meta_repo_names + component_names
    
    for name in all_repo_names:
        repo_path = parent / name
        if repo_path.exists() and repo_path.is_dir() and is_git_repo(repo_path):
            repos.append(repo_path)
    
    return repos


def run_git_operation(repo_path: Path, operation: str, args: List[str] = None) -> bool:
    """Run a git operation in a repository."""
    if args is None:
        args = []
    
    cmd = ["git", "-C", str(repo_path), operation] + args
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            if result.stdout:
                print(result.stdout, end="")
            return True
        else:
            if result.stderr:
                print(result.stderr, end="", file=__import__("sys").stderr)
            return False
    except Exception as e:
        error(f"Failed to run git {operation}: {e}")
        return False


@app.command()
def all(
    message: str = typer.Option("Update repositories", "--message", "-m", help="Commit message"),
    push: bool = typer.Option(True, "--push/--no-push", help="Push to remote after commit"),
    remote: str = typer.Option("origin", "--remote", "-r", help="Remote name"),
    branch: str = typer.Option("main", "--branch", "-b", help="Branch name"),
    meta_repos_only: bool = typer.Option(False, "--meta-repos-only", help="Only update meta-repos"),
    components_only: bool = typer.Option(False, "--components-only", help="Only update component repos"),
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Update all repositories (add, commit, push)."""
    root = find_meta_repo_root()
    if not root:
        error("Could not find meta-repo root. Run from a meta-repo directory.")
        raise typer.Exit(code=1)
    
    parent = root.parent
    
    # Determine which repos to update
    repos_to_update = []
    
    if not components_only:
        # Add meta-repos
        meta_repo_names = ["meta-repo", "gambling-platform-meta", "scraping-platform-meta", "platform-meta"]
        for name in meta_repo_names:
            repo_path = parent / name
            if repo_path.exists() and is_git_repo(repo_path):
                repos_to_update.append(("meta-repo", repo_path))
    
    if not meta_repos_only:
        # Add component repos from manifest
        components = get_components(manifests_dir)
        for comp_name in components.keys():
            # Try both components/ subdirectory and sibling directory
            comp_path = root / "components" / comp_name
            sibling_path = parent / comp_name
            
            if sibling_path.exists() and is_git_repo(sibling_path):
                repos_to_update.append(("component", sibling_path))
            elif comp_path.exists() and is_git_repo(comp_path):
                repos_to_update.append(("component", comp_path))
    
    if not repos_to_update:
        warning("No git repositories found to update.")
        return
    
    log(f"Found {len(repos_to_update)} repository(ies) to update")
    
    # Update each repository
    results = []
    for repo_type, repo_path in repos_to_update:
        repo_name = repo_path.name
        log(f"\n📦 Updating {repo_type}: {repo_name}")
        
        # Check status first
        status_result = run_git_operation(repo_path, "status", ["--porcelain"])
        if not status_result:
            warning(f"  ⚠️  Could not check status for {repo_name}")
            results.append((repo_name, "error", "Could not check status"))
            continue
        
        # Check if there are changes
        result = subprocess.run(
            ["git", "-C", str(repo_path), "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            log(f"  ✓ No changes to commit in {repo_name}")
            results.append((repo_name, "skipped", "No changes"))
            continue
        
        # Add all changes
        log(f"  📝 Adding changes...")
        if not run_git_operation(repo_path, "add", ["."]):
            error(f"  ❌ Failed to add changes in {repo_name}")
            results.append((repo_name, "error", "Failed to add"))
            continue
        
        # Commit
        log(f"  💾 Committing changes...")
        if not run_git_operation(repo_path, "commit", ["-m", message]):
            error(f"  ❌ Failed to commit in {repo_name}")
            results.append((repo_name, "error", "Failed to commit"))
            continue
        
        success(f"  ✅ Committed changes in {repo_name}")
        
        # Push if requested
        if push:
            log(f"  🚀 Pushing to {remote}/{branch}...")
            push_args = [remote, branch]
            if not run_git_operation(repo_path, "push", push_args):
                warning(f"  ⚠️  Failed to push {repo_name} (may not have remote configured)")
                results.append((repo_name, "committed", "Push failed"))
            else:
                success(f"  ✅ Pushed {repo_name}")
                results.append((repo_name, "success", "Committed and pushed"))
        else:
            results.append((repo_name, "committed", "Not pushed (--no-push)"))
    
    # Summary
    log("\n" + "="*60)
    log("Update Summary:")
    log("="*60)
    
    successful = [r for r in results if r[1] == "success"]
    committed = [r for r in results if r[1] == "committed"]
    skipped = [r for r in results if r[1] == "skipped"]
    errors = [r for r in results if r[1] == "error"]
    
    if successful:
        log(f"✅ Successfully updated: {len(successful)}")
        for name, _, _ in successful:
            log(f"   - {name}")
    
    if committed:
        log(f"💾 Committed (not pushed): {len(committed)}")
        for name, _, _ in committed:
            log(f"   - {name}")
    
    if skipped:
        log(f"⏭️  Skipped (no changes): {len(skipped)}")
        for name, _, _ in skipped:
            log(f"   - {name}")
    
    if errors:
        log(f"❌ Errors: {len(errors)}")
        for name, _, msg in errors:
            log(f"   - {name}: {msg}")
    
    if errors:
        raise typer.Exit(code=1)


@app.command()
def status(
    manifests_dir: str = typer.Option("manifests", "--manifests", help="Manifests directory"),
):
    """Show status of all repositories."""
    root = find_meta_repo_root()
    if not root:
        error("Could not find meta-repo root. Run from a meta-repo directory.")
        raise typer.Exit(code=1)
    
    parent = root.parent
    
    # Get all repos
    meta_repos = []
    component_repos = []
    
    # Meta-repos
    meta_repo_names = ["meta-repo", "gambling-platform-meta", "scraping-platform-meta", "platform-meta"]
    for name in meta_repo_names:
        repo_path = parent / name
        if repo_path.exists() and is_git_repo(repo_path):
            meta_repos.append(repo_path)
    
    # Component repos
    components = get_components(manifests_dir)
    for comp_name in components.keys():
        sibling_path = parent / comp_name
        comp_path = root / "components" / comp_name
        
        if sibling_path.exists() and is_git_repo(sibling_path):
            component_repos.append(sibling_path)
        elif comp_path.exists() and is_git_repo(comp_path):
            component_repos.append(comp_path)
    
    log(f"Found {len(meta_repos)} meta-repo(s) and {len(component_repos)} component repo(s)")
    
    # Show status for each
    from meta.utils.logger import table
    
    rows = []
    for repo_path in meta_repos + component_repos:
        repo_name = repo_path.name
        repo_type = "meta-repo" if repo_path in meta_repos else "component"
        
        # Get git status
        result = subprocess.run(
            ["git", "-C", str(repo_path), "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        
        has_changes = bool(result.stdout.strip())
        status_icon = "📝" if has_changes else "✓"
        status_text = "Has changes" if has_changes else "Clean"
        
        rows.append([status_icon, repo_name, repo_type, status_text])
    
    table(["Status", "Repository", "Type", "State"], rows)

