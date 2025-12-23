"""Changeset commands for atomic cross-repo operations."""

import typer
import subprocess
from pathlib import Path
from typing import Optional, List
from meta.utils.logger import log, success, error, warning, table, panel
from meta.utils.changeset import (
    create_changeset, load_changeset, list_changesets, save_changeset,
    find_changeset_by_commit, extract_changeset_id_from_message,
    get_current_changeset, CHANGESET_DIR
)
from meta.utils.manifest import find_meta_repo_root, get_components
from meta.utils.git import get_commit_sha, get_current_version

app = typer.Typer(help="Changeset management for atomic cross-repo operations")


@app.command()
def create(
    description: str = typer.Argument(..., help="Changeset description"),
    author: Optional[str] = typer.Option(None, "--author", "-a", help="Author name"),
):
    """Create a new changeset."""
    changeset = create_changeset(description, author)
    success(f"Created changeset: {changeset.id}")
    log(f"Description: {description}")
    log(f"Status: {changeset.status}")
    log(f"\nUse this ID in commit messages: [changeset:{changeset.id}]")
    log(f"Or use: meta git commit -m 'message' --changeset {changeset.id}")


@app.command()
def show(
    changeset_id: str = typer.Argument(..., help="Changeset ID"),
):
    """Show details of a changeset."""
    changeset = load_changeset(changeset_id)
    
    if not changeset:
        error(f"Changeset not found: {changeset_id}")
        raise typer.Exit(code=1)
    
    panel(f"Changeset: {changeset.id}", "Changeset Details")
    
    log(f"Description: {changeset.description}")
    log(f"Author: {changeset.author}")
    log(f"Timestamp: {changeset.timestamp}")
    log(f"Status: {changeset.status}")
    
    if changeset.repos:
        log(f"\nRepositories ({len(changeset.repos)}):")
        rows = []
        for repo in changeset.repos:
            rows.append([
                repo["name"],
                repo["commit"][:8] if len(repo["commit"]) > 8 else repo["commit"],
                repo["branch"],
                repo["message"][:50] + "..." if len(repo["message"]) > 50 else repo["message"]
            ])
        table(["Repository", "Commit", "Branch", "Message"], rows)
    else:
        log("\nNo commits yet")
    
    if changeset.metadata:
        log(f"\nMetadata:")
        for key, value in changeset.metadata.items():
            log(f"  {key}: {value}")


@app.command()
def list(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of changesets to show"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
):
    """List changesets."""
    changesets = list_changesets(limit=limit, status_filter=status)
    
    if not changesets:
        log("No changesets found")
        return
    
    panel(f"Changesets ({len(changesets)})", "Changeset List")
    
    rows = []
    for cs in changesets:
        status_icon = {
            "in-progress": "🔄",
            "committed": "✅",
            "failed": "❌",
            "rolled-back": "↩️"
        }.get(cs.status, "❓")
        
        rows.append([
            status_icon,
            cs.id,
            cs.description[:40] + "..." if len(cs.description) > 40 else cs.description,
            cs.status,
            str(len(cs.repos)),
            cs.timestamp[:10] if len(cs.timestamp) > 10 else cs.timestamp
        ])
    
    table(["Status", "ID", "Description", "Status", "Repos", "Date"], rows)


@app.command()
def finalize(
    changeset_id: Optional[str] = typer.Option(None, "--id", "-i", help="Changeset ID (uses current if not specified)"),
):
    """Finalize a changeset (mark as committed)."""
    if not changeset_id:
        changeset = get_current_changeset()
        if not changeset:
            error("No in-progress changeset found. Specify --id")
            raise typer.Exit(code=1)
        changeset_id = changeset.id
    else:
        changeset = load_changeset(changeset_id)
        if not changeset:
            error(f"Changeset not found: {changeset_id}")
            raise typer.Exit(code=1)
    
    changeset.status = "committed"
    save_changeset(changeset)
    success(f"Finalized changeset: {changeset_id}")


@app.command()
def rollback(
    changeset_id: str = typer.Argument(..., help="Changeset ID to rollback"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be rolled back without doing it"),
):
    """Rollback a changeset across all repos."""
    changeset = load_changeset(changeset_id)
    
    if not changeset:
        error(f"Changeset not found: {changeset_id}")
        raise typer.Exit(code=1)
    
    if changeset.status == "rolled-back":
        warning(f"Changeset {changeset_id} is already rolled back")
        return
    
    if not changeset.repos:
        warning(f"Changeset {changeset_id} has no commits to rollback")
        return
    
    panel(f"Rollback: {changeset_id}", "Rollback Plan")
    log(f"Description: {changeset.description}")
    log(f"Repositories to rollback: {len(changeset.repos)}")
    
    if dry_run:
        log("\n[DRY RUN] Would rollback:")
        for repo in reversed(changeset.repos):  # Reverse order
            log(f"  {repo['name']}: {repo['commit'][:8]} - {repo['message']}")
        return
    
    # Rollback in reverse order (dependency order)
    root = find_meta_repo_root()
    if not root:
        error("Could not find meta-repo root")
        raise typer.Exit(code=1)
    
    parent = root.parent
    
    for repo in reversed(changeset.repos):
        repo_name = repo["name"]
        commit_sha = repo["commit"]
        
        # Try to find repo path
        repo_path = parent / repo_name
        if not repo_path.exists():
            repo_path = root / "components" / repo_name
        
        if not repo_path.exists():
            warning(f"Repository {repo_name} not found, skipping")
            continue
        
        log(f"\nRolling back {repo_name}...")
        
        # Create revert commit
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_path), "revert", "--no-edit", commit_sha],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                success(f"Reverted {repo_name}")
            else:
                error(f"Failed to revert {repo_name}: {result.stderr}")
        except Exception as e:
            error(f"Error reverting {repo_name}: {e}")
    
    # Mark changeset as rolled back
    changeset.status = "rolled-back"
    save_changeset(changeset)
    
    success(f"Rollback completed for changeset: {changeset_id}")


@app.command()
def bisect(
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start changeset ID"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="End changeset ID"),
    test_command: str = typer.Option("meta test --all", "--test", "-t", help="Test command to run"),
):
    """Bisect to find which changeset introduced a bug."""
    if not start or not end:
        error("Both --start and --end changeset IDs are required")
        raise typer.Exit(code=1)
    
    start_cs = load_changeset(start)
    end_cs = load_changeset(end)
    
    if not start_cs or not end_cs:
        error("Invalid changeset ID(s)")
        raise typer.Exit(code=1)
    
    # Get all changesets between start and end
    all_changesets = list_changesets()
    start_idx = None
    end_idx = None
    
    for i, cs in enumerate(all_changesets):
        if cs.id == start:
            start_idx = i
        if cs.id == end:
            end_idx = i
    
    if start_idx is None or end_idx is None:
        error("Could not find changesets in index")
        raise typer.Exit(code=1)
    
    if start_idx < end_idx:
        start_idx, end_idx = end_idx, start_idx
    
    changesets_to_test = all_changesets[end_idx:start_idx+1]
    
    log(f"Bisecting {len(changesets_to_test)} changesets...")
    log(f"Test command: {test_command}")
    
    # Binary search
    left = 0
    right = len(changesets_to_test) - 1
    bad_changeset = None
    
    while left <= right:
        mid = (left + right) // 2
        test_cs = changesets_to_test[mid]
        
        log(f"\nTesting changeset {test_cs.id} ({mid+1}/{len(changesets_to_test)})...")
        
        # Checkout this changeset
        root = find_meta_repo_root()
        if root:
            # Apply changeset (checkout all commits)
            for repo in test_cs.repos:
                repo_path = root.parent / repo["name"]
                if not repo_path.exists():
                    repo_path = root / "components" / repo["name"]
                
                if repo_path.exists():
                    subprocess.run(
                        ["git", "-C", str(repo_path), "checkout", repo["commit"]],
                        capture_output=True
                    )
        
        # Run test
        result = subprocess.run(
            test_command.split(),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            log(f"  ❌ Test failed")
            bad_changeset = test_cs
            right = mid - 1
        else:
            log(f"  ✅ Test passed")
            left = mid + 1
    
    if bad_changeset:
        panel(f"Found: {bad_changeset.id}", "Bisect Result")
        log(f"Description: {bad_changeset.description}")
        log(f"First failing changeset: {bad_changeset.id}")
    else:
        log("No failing changeset found in range")


@app.command()
def current():
    """Show the current in-progress changeset."""
    changeset = get_current_changeset()
    
    if not changeset:
        log("No in-progress changeset")
        return
    
    show(changeset.id)


