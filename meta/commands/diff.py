"""Lock file diff commands."""

import typer
from meta.utils.logger import log, success, error, table, panel
from meta.utils.diff import diff_lock_files, diff_environments

app = typer.Typer(help="Compare lock files and environments")


@app.command()
def lock(
    lock_file1: str = typer.Argument(..., help="First lock file"),
    lock_file2: str = typer.Argument(..., help="Second lock file"),
):
    """Compare two lock files."""
    differences = diff_lock_files(lock_file1, lock_file2)
    
    if not differences:
        return
    
    panel(f"Lock File Comparison", "Diff")
    
    if differences.get("only_in_file1"):
        log(f"\nOnly in {lock_file1}:")
        for comp in differences["only_in_file1"]:
            log(f"  - {comp}")
    
    if differences.get("only_in_file2"):
        log(f"\nOnly in {lock_file2}:")
        for comp in differences["only_in_file2"]:
            log(f"  - {comp}")
    
    if differences.get("version_differences"):
        log("\nVersion Differences:")
        rows = []
        for diff in differences["version_differences"]:
            rows.append([
                diff["component"],
                diff["file1_version"],
                diff["file2_version"]
            ])
        table(["Component", lock_file1, lock_file2], rows)
    
    if differences.get("commit_differences"):
        log("\nCommit Differences:")
        rows = []
        for diff in differences["commit_differences"]:
            rows.append([
                diff["component"],
                diff["file1_commit"] or "N/A",
                diff["file2_commit"] or "N/A"
            ])
        table(["Component", lock_file1, lock_file2], rows)


@app.command()
def env(
    env1: str = typer.Argument(..., help="First environment"),
    env2: str = typer.Argument(..., help="Second environment"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Compare lock files for two environments."""
    differences = diff_environments(env1, env2, manifests_dir)
    
    if not differences:
        return
    
    panel(f"Environment Lock File Comparison: {env1} vs {env2}", "Diff")
    
    total_diffs = (
        len(differences.get("only_in_file1", [])) +
        len(differences.get("only_in_file2", [])) +
        len(differences.get("version_differences", [])) +
        len(differences.get("commit_differences", []))
    )
    
    if total_diffs == 0:
        success("No differences between environments")
        return
    
    log(f"Found {total_diffs} difference(s)")
    
    # Show differences (same format as lock command)
    if differences.get("version_differences"):
        rows = []
        for diff in differences["version_differences"]:
            rows.append([
                diff["component"],
                diff["file1_version"],
                diff["file2_version"]
            ])
        table(["Component", env1, env2], rows)


