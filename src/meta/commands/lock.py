"""Generate and manage lock files."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.lock import generate_lock_file, validate_lock_file
from meta.utils.environment_locks import (
    generate_environment_lock_file,
    validate_environment_lock_file,
    promote_lock_file,
    compare_lock_files,
    get_environment_lock_file_path
)

app = typer.Typer(help="Generate and manage lock files")


@app.callback(invoke_without_command=True)
def lock(
    ctx: typer.Context,
    env: Optional[str] = typer.Option(None, "--env", "-e", help="Environment to generate lock file for (creates environment-specific lock file)"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    lock_file: str = typer.Option("manifests/components.lock.yaml", "--lock-file", "-l", help="Lock file path (ignored if --env is used)"),
    validate: bool = typer.Option(False, "--validate", help="Validate lock file after generation"),
    changeset: Optional[str] = typer.Option(None, "--changeset", help="Associate lock file generation with a changeset"),
):
    """Generate a lock file with exact commit SHAs for reproducible builds."""
    if ctx.invoked_subcommand is None:
        if env:
            # Generate environment-specific lock file
            log(f"Generating lock file for environment: {env}")
            if not generate_environment_lock_file(env, manifests_dir):
                error("Failed to generate environment lock file")
                raise typer.Exit(code=1)
            
            if validate:
                log("Validating generated lock file...")
                if not validate_environment_lock_file(env, manifests_dir):
                    error("Lock file validation failed")
                    raise typer.Exit(code=1)
                success("Lock file is valid")
            
            lock_file_path = get_environment_lock_file_path(env, manifests_dir)
            success("Lock file generated successfully!")
            log(f"Lock file saved to: {lock_file_path}")
        else:
            # Generate default lock file
            log("Generating lock file for reproducible builds...")
            if not generate_lock_file(manifests_dir, lock_file):
                error("Failed to generate lock file")
                raise typer.Exit(code=1)
            
            if validate:
                log("Validating generated lock file...")
                if not validate_lock_file(manifests_dir, lock_file):
                    error("Lock file validation failed")
                    raise typer.Exit(code=1)
                success("Lock file is valid")
            
            success("Lock file generated successfully!")
            log(f"Lock file saved to: {lock_file}")
        
        # Track in changeset if provided
        if changeset:
            from meta.utils.changeset import load_changeset, save_changeset
            from meta.utils.manifest import find_meta_repo_root
            from meta.utils.git import get_commit_sha
            from pathlib import Path
            import subprocess
            
            cs = load_changeset(changeset)
            if cs:
                root = find_meta_repo_root()
                if root:
                    # Get commit SHA after lock file is committed
                    commit_sha = get_commit_sha(str(root))
                    if commit_sha:
                        result = subprocess.run(
                            ["git", "-C", str(root), "branch", "--show-current"],
                            capture_output=True,
                            text=True
                        )
                        branch = result.stdout.strip() or "main"
                        
                        cs.add_repo_commit(
                            repo_name=root.name,
                            repo_url="",
                            commit_sha=commit_sha,
                            branch=branch,
                            message=f"Update lock file [changeset:{changeset}]"
                        )
                        save_changeset(cs)
                        log(f"Lock file generation tracked in changeset {changeset}")
        
        log("Commit this file to ensure reproducible builds across environments")


@app.command()
def validate(
    env: Optional[str] = typer.Option(None, "--env", "-e", help="Environment to validate (validates environment-specific lock file)"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    lock_file: str = typer.Option("manifests/components.lock.yaml", "--lock-file", "-l", help="Lock file path (ignored if --env is used)"),
):
    """Validate that lock file matches current components manifest."""
    if env:
        log(f"Validating lock file for environment: {env}")
        if not validate_environment_lock_file(env, manifests_dir):
            error("Lock file validation failed")
            raise typer.Exit(code=1)
    else:
        log("Validating lock file...")
        if not validate_lock_file(manifests_dir, lock_file):
            error("Lock file validation failed")
            raise typer.Exit(code=1)
    
    success("Lock file is valid!")


@app.command()
def promote(
    from_env: str = typer.Argument(..., help="Source environment"),
    to_env: str = typer.Argument(..., help="Target environment"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Promote lock file from one environment to another."""
    if not promote_lock_file(from_env, to_env, manifests_dir):
        error("Failed to promote lock file")
        raise typer.Exit(code=1)
    
    success(f"Lock file promoted from {from_env} to {to_env}")


@app.command()
def compare(
    env1: str = typer.Argument(..., help="First environment"),
    env2: str = typer.Argument(..., help="Second environment"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Compare lock files between two environments."""
    log(f"Comparing lock files: {env1} vs {env2}")
    
    differences = compare_lock_files(env1, env2, manifests_dir)
    
    if "error" in differences:
        error(differences["error"])
        raise typer.Exit(code=1)
    
    if differences["only_in_env1"]:
        panel(f"Only in {env1}", "Components")
        for comp in differences["only_in_env1"]:
            log(f"  - {comp}")
    
    if differences["only_in_env2"]:
        panel(f"Only in {env2}", "Components")
        for comp in differences["only_in_env2"]:
            log(f"  - {comp}")
    
    if differences["version_differences"]:
        panel("Version Differences", "Components")
        rows = []
        for diff in differences["version_differences"]:
            rows.append([
                diff["component"],
                diff[f"{env1}_version"],
                diff[f"{env2}_version"]
            ])
        table(["Component", f"{env1} Version", f"{env2} Version"], rows)
    
    if differences["commit_differences"]:
        panel("Commit Differences", "Components")
        rows = []
        for diff in differences["commit_differences"]:
            rows.append([
                diff["component"],
                diff[f"{env1}_commit"],
                diff[f"{env2}_commit"]
            ])
        table(["Component", f"{env1} Commit", f"{env2} Commit"], rows)
    
    if not any([differences["only_in_env1"], differences["only_in_env2"], 
                differences["version_differences"], differences["commit_differences"]]):
        success("Lock files are identical!")

