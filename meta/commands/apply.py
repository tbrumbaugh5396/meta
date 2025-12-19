"""Apply changes to meta-repo."""

import typer
from pathlib import Path
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.manifest import get_components, get_environment_config
from meta.utils.git import clone_repo, checkout_version, pull_latest, get_commit_sha
from meta.utils.bazel import run_bazel_build, run_bazel_test
from meta.utils.lock import get_locked_components
from meta.utils.environment_locks import get_environment_lock_file_path, load_environment_lock_file
from meta.utils.packages import install_component_dependencies
from meta.utils.dependencies import get_dependency_order
from meta.utils.progress import ProgressBar
from meta.utils.config import get_config
from meta.utils.error_recovery import ErrorRecoveryContext, execute_with_recovery
from meta.commands.plan import compute_changes
import concurrent.futures
from typing import List, Tuple

app = typer.Typer(help="Apply changes to meta-repo")


def apply_component(name: str, comp: dict, env: str, manifests_dir: str = "manifests", 
                    use_lock: bool = False, lock_file: str = "manifests/components.lock.yaml",
                    skip_packages: bool = False) -> bool:
    """Apply changes for a single component."""
    log(f"Applying changes for component: {name}")
    
    comp_type = comp.get("type", "unknown")
    version = comp.get("version", "latest")
    repo_url = comp.get("repo", "")
    build_target = comp.get("build_target", "")
    
    if not repo_url:
        error(f"No repository URL specified for {name}")
        return False
    
    # If using lock file, get exact commit SHA
    if use_lock:
        locked_components = get_locked_components(lock_file)
        if name in locked_components:
            locked = locked_components[name]
            commit_sha = locked.get("commit")
            if commit_sha:
                log(f"Using locked commit: {commit_sha[:8]}")
                version = commit_sha  # Use commit SHA instead of tag
    
    # Determine component directory
    comp_dir = f"components/{name}"
    comp_path = Path(comp_dir)
    
    # Clone or update repository
    if comp_path.exists():
        log(f"Component {name} already exists, updating...")
        if not pull_latest(comp_dir):
            error(f"Failed to update {name}")
            return False
    else:
        if not clone_repo(repo_url, comp_dir, version):
            error(f"Failed to clone {name}")
            return False
    
    # Checkout specific version/commit if needed
    if version and version != "latest":
        if not checkout_version(comp_dir, version):
            error(f"Failed to checkout version {version} for {name}")
            return False
    
    # Install package manager dependencies
    if not install_component_dependencies(comp_dir, skip_packages):
        error(f"Failed to install dependencies for {name}")
        return False
    
    # Build/test if Bazel component
    if comp_type == "bazel" and build_target:
        log(f"Building Bazel target: {build_target}")
        if not run_bazel_build(build_target, comp_dir):
            error(f"Failed to build {name}")
            return False
        
        log(f"Testing Bazel target: {build_target}")
        if not run_bazel_test(build_target, comp_dir):
            error(f"Failed to test {name}")
            return False
    
    success(f"Successfully applied changes for {name}")
    return True


@app.callback(invoke_without_command=True)
def apply(
    ctx: typer.Context,
    env: Optional[str] = typer.Option(None, "--env", "-e", help="Environment to apply to"),
    manifests_dir: Optional[str] = typer.Option(None, "--manifests", "-m", help="Manifests directory"),
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Apply for specific component only"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Apply all components (even unchanged ones)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done without making changes"),
    locked: bool = typer.Option(False, "--locked", help="Use lock file for exact commit SHAs"),
    lock_file: str = typer.Option("manifests/components.lock.yaml", "--lock-file", "-l", help="Lock file path"),
    skip_packages: bool = typer.Option(False, "--skip-packages", help="Skip package manager dependency installation"),
    parallel: bool = typer.Option(None, "--parallel/--no-parallel", "-p", help="Apply components in parallel"),
    jobs: Optional[int] = typer.Option(None, "--jobs", "-j", help="Number of parallel jobs"),
    progress: Optional[bool] = typer.Option(None, "--progress/--no-progress", help="Show progress bar"),
    continue_on_error: bool = typer.Option(False, "--continue-on-error", help="Continue on component failures"),
    retry: int = typer.Option(3, "--retry", help="Number of retry attempts"),
    retry_backoff: float = typer.Option(2.0, "--retry-backoff", help="Retry backoff multiplier"),
):
    """Deploy or sync components to target environment."""
    # Only run if no subcommands were invoked
    if ctx.invoked_subcommand is None:
        # Load config for defaults
        config = get_config()
        if env is None:
            env = config.get("default_env", "dev")
        if manifests_dir is None:
            manifests_dir = config.get("manifests_dir", "manifests")
        if parallel is None:
            parallel = config.get("parallel", False)
        if jobs is None:
            jobs = config.get("parallel_jobs", 4)
        if progress is None:
            progress = config.get("show_progress", True)
        
        log(f"Applying changes for environment: {env}")
        
        if dry_run:
            log("DRY RUN MODE - No changes will be made")
            changes = compute_changes(env, manifests_dir)
            
            if component:
                all_changes = changes["upgrades"] + changes["downgrades"] + changes["new"] + changes["unchanged"]
                filtered = [c for c in all_changes if c.get("component") == component]
                if not filtered:
                    log(f"No changes planned for component: {component}")
                    return
                changes = {
                    "upgrades": [c for c in changes["upgrades"] if c["component"] == component],
                    "downgrades": [c for c in changes["downgrades"] if c["component"] == component],
                    "new": [c for c in changes["new"] if c["component"] == component],
                    "unchanged": [c for c in changes["unchanged"] if c["component"] == component]
                }
            
            if changes["upgrades"]:
                panel("Would upgrade", "Upgrades")
                rows = [[c["component"], c["current"], "→", c["desired"]] for c in changes["upgrades"]]
                table(["Component", "Current", "", "Desired"], rows)
            
            if changes["new"]:
                panel("Would clone", "New")
                rows = [[c["component"], c["version"], c["type"]] for c in changes["new"]]
                table(["Component", "Version", "Type"], rows)
            
            return
        
        components = get_components(manifests_dir)
        changes = compute_changes(env, manifests_dir)
        
        # Determine which components to apply
        components_to_apply = []
        if component:
            if component not in components:
                error(f"Component {component} not found")
                raise typer.Exit(code=1)
            components_to_apply = [component]
        elif all_components:
            # Apply ALL components explicitly
            components_to_apply = list(components.keys())
        else:
            # Apply all components with changes or new components (default behavior)
            all_changes = changes["upgrades"] + changes["downgrades"] + changes["new"]
            components_to_apply = [c["component"] for c in all_changes]
            
            # Also apply unchanged components if they don't exist locally
            for unchanged in changes["unchanged"]:
                comp_name = unchanged["component"]
                comp_path = Path(f"components/{comp_name}")
                if not comp_path.exists():
                    components_to_apply.append(comp_name)
        
        if not components_to_apply:
            log("No components to apply")
            return
        
        # If using lock file, validate it exists
        if locked:
            from pathlib import Path as PathLib
            # Use environment-specific lock file if available
            if env and env != "dev":
                env_lock_file = get_environment_lock_file_path(env, manifests_dir)
                env_lock_path = PathLib(env_lock_file)
                if env_lock_path.exists():
                    lock_file = env_lock_file
                    log(f"Using environment-specific lock file: {lock_file}")
            
            lock_path = PathLib(lock_file)
            if not lock_path.exists():
                error(f"Lock file not found: {lock_file}")
                if env:
                    error(f"Run 'meta lock --env {env}' to generate a lock file for this environment")
                else:
                    error("Run 'meta lock' to generate a lock file first")
                raise typer.Exit(code=1)
        
        # Get dependency order to apply components in correct order
        dependency_order = get_dependency_order(components)
        
        # Filter to only components we're applying, maintaining dependency order
        ordered_to_apply = [name for name in dependency_order if name in components_to_apply]
        # Add any components not in dependency order (shouldn't happen, but be safe)
        for name in components_to_apply:
            if name not in ordered_to_apply:
                ordered_to_apply.append(name)
        
        # Apply each component in dependency order
        all_success = True
        
        if parallel and len(ordered_to_apply) > 1:
            # Parallel execution
            log(f"Applying {len(ordered_to_apply)} components in parallel (jobs={jobs})")
            
            def apply_with_name(comp_name: str) -> Tuple[str, bool]:
                comp = components[comp_name]
                success = apply_component(comp_name, comp, env, manifests_dir, use_lock=locked,
                                        lock_file=lock_file, skip_packages=skip_packages)
                return (comp_name, success)
            
            if progress:
                from meta.utils.progress import with_progress
                results = with_progress(ordered_to_apply, "Applying components", apply_with_name)
            else:
                with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
                    results = list(executor.map(apply_with_name, ordered_to_apply))
            
            for comp_name, success_result in results:
                if not success_result:
                    all_success = False
        else:
            # Sequential execution
            progress_bar = None
            if progress and len(ordered_to_apply) > 1:
                progress_bar = ProgressBar(len(ordered_to_apply), "Applying components")
            
            for comp_name in ordered_to_apply:
                comp = components[comp_name]
                if not apply_component(comp_name, comp, env, manifests_dir, use_lock=locked, 
                                     lock_file=lock_file, skip_packages=skip_packages):
                    all_success = False
                
                if progress_bar:
                    progress_bar.update(1)
            
            if progress_bar:
                progress_bar.finish()
        
        if all_success:
            success("All components applied successfully!")
        else:
            error("Some components failed to apply")
            raise typer.Exit(code=1)

