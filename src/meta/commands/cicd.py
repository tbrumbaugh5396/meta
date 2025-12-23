"""CI/CD template commands."""

import typer
import subprocess
import shutil
import json
import yaml
from pathlib import Path
from typing import Optional, List, Set
from meta.utils.logger import log, success, error, warning
from meta.utils.cicd_templates import scaffold_cicd, validate_cicd, generate_cicd_template
from meta.utils.manifest import get_components, find_meta_repo_root

app = typer.Typer(help="CI/CD template management")


@app.command()
def scaffold(
    component: str = typer.Argument(..., help="Component name"),
    provider: str = typer.Argument(..., help="CI/CD provider (github/gitlab/jenkins)"),
):
    """Scaffold CI/CD configuration for a component."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = Path(f"components/{component}")
    
    if not component_path.exists():
        error(f"Component directory not found: {component_path}")
        raise typer.Exit(code=1)
    
    if scaffold_cicd(component, provider, component_path):
        success(f"Scaffolded CI/CD config for {component}")
    else:
        error("Failed to scaffold CI/CD config")
        raise typer.Exit(code=1)


@app.command()
def validate(
    component: str = typer.Argument(..., help="Component name"),
):
    """Validate CI/CD configuration."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        raise typer.Exit(code=1)
    
    component_path = Path(f"components/{component}")
    
    if validate_cicd(component, component_path):
        success(f"CI/CD configuration valid for {component}")
    else:
        error("CI/CD configuration not found or invalid")
        raise typer.Exit(code=1)


def parse_workflow_for_images(workflow_path: Path) -> Set[str]:
    """Parse a workflow YAML file to extract required Docker images."""
    images = set()
    
    try:
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        if not workflow or 'jobs' not in workflow:
            return images
        
        # Map of runs-on values to act Docker images
        runner_image_map = {
            'ubuntu-latest': 'catthehacker/ubuntu:act-latest',
            'ubuntu-22.04': 'catthehacker/ubuntu:act-22.04',
            'ubuntu-20.04': 'catthehacker/ubuntu:act-20.04',
            'windows-latest': 'catthehacker/windows-server:act-latest',
            'macos-latest': 'catthehacker/macos:act-latest',
            'macos-12': 'catthehacker/macos:act-12',
            'macos-13': 'catthehacker/macos:act-13',
        }
        
        for job_name, job_config in workflow.get('jobs', {}).items():
            runs_on = job_config.get('runs-on')
            if runs_on:
                # Handle matrix strategies
                if isinstance(runs_on, dict) and 'matrix' in runs_on:
                    # For matrix, we'll use the base runner
                    continue
                
                # Handle list of runners (e.g., [self-hosted, linux])
                if isinstance(runs_on, list):
                    for runner in runs_on:
                        if isinstance(runner, str) and runner in runner_image_map:
                            images.add(runner_image_map[runner])
                elif isinstance(runs_on, str):
                    # Direct runner name
                    if runs_on in runner_image_map:
                        images.add(runner_image_map[runs_on])
                    # Also check for container: syntax
                    elif 'container:' in runs_on:
                        # Extract container image
                        container_image = runs_on.split('container:')[1].strip()
                        images.add(container_image)
            
            # Check for container jobs
            container = job_config.get('container')
            if container:
                if isinstance(container, str):
                    images.add(container)
                elif isinstance(container, dict) and 'image' in container:
                    images.add(container['image'])
        
        return images
    except Exception as e:
        warning(f"Could not parse workflow {workflow_path}: {e}")
        return images


def check_docker_image_exists(image: str) -> bool:
    """Check if a Docker image exists locally."""
    try:
        result = subprocess.run(
            ["docker", "images", "-q", image],
            capture_output=True,
            text=True,
            timeout=5
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def pull_docker_image(image: str, progress: bool = True, max_retries: int = 3) -> bool:
    """Pull a Docker image if it doesn't exist locally."""
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.console import Console
    import time
    
    if check_docker_image_exists(image):
        return True
    
    log(f"Pulling Docker image: {image} (this may take a while, ~17GB for act-latest)...")
    
    for attempt in range(1, max_retries + 1):
        if attempt > 1:
            log(f"Retry attempt {attempt}/{max_retries} for {image}...")
            time.sleep(2)  # Brief delay before retry
        
        try:
            if progress:
                console = Console()
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    console=console
                ) as progress_bar:
                    task = progress_bar.add_task(
                        f"Pulling {image} (attempt {attempt}/{max_retries})...",
                        total=None
                    )
                    
                    # Don't capture output - let Docker show progress in real-time
                    result = subprocess.run(
                        ["docker", "pull", image],
                        stderr=subprocess.STDOUT
                    )
                    
                    progress_bar.update(task, completed=True)
            else:
                # Show output directly when not using progress bar
                result = subprocess.run(["docker", "pull", image])
            
            if result.returncode == 0:
                success(f"✅ Successfully pulled {image}")
                return True
            else:
                # Check if it's a network error
                if attempt < max_retries:
                    warning(f"⚠️  Pull failed (attempt {attempt}/{max_retries}), retrying...")
                    continue
                else:
                    error(f"❌ Failed to pull {image} after {max_retries} attempts")
                    error("This might be due to:")
                    error("  - Network connectivity issues")
                    error("  - Docker daemon connection problems")
                    error("  - Insufficient disk space")
                    error("")
                    error("You can try manually: docker pull " + image)
                    return False
                    
        except KeyboardInterrupt:
            error("\n❌ Pull interrupted by user")
            return False
        except Exception as e:
            if attempt < max_retries:
                warning(f"⚠️  Error during pull (attempt {attempt}/{max_retries}): {e}")
                continue
            else:
                error(f"❌ Failed to pull {image}: {e}")
                return False
    
    return False


def ensure_required_images(workflows_to_run: List[str], cwd: Path, progress: bool = True, 
                          allow_partial: bool = False) -> bool:
    """Ensure all required Docker images for workflows are available."""
    all_images = set()
    
    # Collect images from all workflows
    for wf in workflows_to_run:
        if not Path(wf).is_absolute():
            wf_path = cwd / wf
        else:
            wf_path = Path(wf)
        
        if wf_path.exists():
            images = parse_workflow_for_images(wf_path)
            all_images.update(images)
    
    if not all_images:
        # Default to ubuntu-latest if no images found
        all_images.add('catthehacker/ubuntu:act-latest')
        log("No specific images found in workflows, using default: catthehacker/ubuntu:act-latest")
    
    # Check and pull missing images
    missing_images = [img for img in all_images if not check_docker_image_exists(img)]
    
    if missing_images:
        log(f"Found {len(missing_images)} missing Docker image(s)")
        failed_images = []
        for image in missing_images:
            if not pull_docker_image(image, progress, max_retries=3):
                failed_images.append(image)
        
        if failed_images:
            if allow_partial:
                warning(f"⚠️  Failed to pull {len(failed_images)} image(s): {', '.join(failed_images)}")
                warning("⚠️  Continuing anyway - act may still work with partial images")
                return True
            else:
                error(f"❌ Failed to pull {len(failed_images)} required image(s)")
                return False
    
    return True


@app.command()
def test(
    workflow: Optional[str] = typer.Option(None, "--workflow", "-w", help="Specific workflow file to test (e.g., .github/workflows/meta-apply.yml)"),
    job: Optional[str] = typer.Option(None, "--job", "-j", help="Specific job to run"),
    event: str = typer.Option("push", "--event", "-e", help="GitHub event to simulate (push, pull_request, workflow_dispatch)"),
    env: Optional[str] = typer.Option(None, "--env", help="Environment for workflow_dispatch inputs"),
    list_only: bool = typer.Option(False, "--list", "-l", help="List available workflows and jobs"),
    secrets_file: Optional[str] = typer.Option(None, "--secrets-file", help="Path to secrets file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would run without executing"),
    all_workflows: bool = typer.Option(False, "--all-workflows", help="Run all workflows"),
    all_jobs: bool = typer.Option(False, "--all-jobs", help="Run all jobs in the workflow(s)"),
    progress: bool = typer.Option(True, "--progress/--no-progress", help="Show progress bars"),
    pull_images: bool = typer.Option(True, "--pull-images/--no-pull-images", help="Automatically pull missing Docker images"),
):
    """Test CI/CD pipeline locally using act (GitHub Actions runner)."""
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.live import Live
    
    # Check if act is installed
    act_path = shutil.which("act")
    if not act_path:
        error("'act' is not installed. Install it with: brew install act")
        error("Or visit: https://github.com/nektos/act")
        error("Or use: meta cicd setup github")
        raise typer.Exit(code=1)
    
    # Find meta-repo root
    root = find_meta_repo_root()
    if root:
        workflows_dir = root / ".github" / "workflows"
        cwd = root
    else:
        workflows_dir = Path(".github/workflows")
        cwd = Path.cwd()
    
    if not workflows_dir.exists():
        error(f"No .github/workflows directory found at {workflows_dir}")
        error("Make sure you're in a meta-repo directory or have GitHub Actions workflows set up")
        raise typer.Exit(code=1)
    
    if list_only:
        log("Available workflows and jobs:")
        result = subprocess.run(
            ["act", "-l"],
            cwd=cwd,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(result.stdout)
        else:
            error(f"Failed to list workflows: {result.stderr}")
            if "Docker" in result.stderr or "docker" in result.stderr:
                warning("Make sure Docker is running")
            raise typer.Exit(code=1)
        return
    
    # Get list of jobs if --all-jobs is specified
    jobs_to_run = []
    if all_jobs:
        # Get list of all jobs from workflows
        result = subprocess.run(
            ["act", "-l"],
            cwd=cwd,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Parse output to extract job names
            lines = result.stdout.split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    # Format is usually: Event JobID
                    # JobID format is usually: WorkflowName/JobName
                    job_id = parts[1] if len(parts) > 1 else ""
                    if "/" in job_id:
                        job_name = job_id.split("/")[-1]
                        if job_name and job_name not in jobs_to_run:
                            jobs_to_run.append(job_name)
            if not jobs_to_run:
                error("No jobs found in workflows")
                raise typer.Exit(code=1)
            log(f"Found {len(jobs_to_run)} job(s) to run: {', '.join(jobs_to_run)}")
        else:
            error("Failed to list workflows")
            raise typer.Exit(code=1)
    elif job:
        jobs_to_run = [job]
    
    # Get all workflow files if --all-workflows is specified
    workflows_to_run = []
    if all_workflows:
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        if not workflow_files:
            error("No workflow files found")
            raise typer.Exit(code=1)
        workflows_to_run = [str(f.relative_to(cwd)) for f in workflow_files]
        log(f"Found {len(workflows_to_run)} workflow(s) to run")
    elif workflow:
        workflows_to_run = [workflow]
    elif not all_jobs and not job:
        # If no workflow specified and no job specified, we need at least one
        error("Specify --workflow, --job, --all-workflows, or --all-jobs")
        raise typer.Exit(code=1)
    
    # If --all-jobs but no workflow specified, find workflows that contain those jobs
    if all_jobs and not workflows_to_run:
        result = subprocess.run(
            ["act", "-l"],
            cwd=cwd,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Extract unique workflow names
            lines = result.stdout.split('\n')
            workflow_set = set()
            for line in lines:
                parts = line.split()
                if len(parts) >= 2 and "/" in parts[1]:
                    wf_name = parts[1].split("/")[0]
                    if wf_name and wf_name not in ("Event", "JobID", "---", ""):
                        workflow_set.add(wf_name)
            workflows_to_run = list(workflow_set)
            if workflows_to_run:
                log(f"Found {len(workflows_to_run)} workflow(s) with jobs")
    
    # Build base act command
    base_cmd = ["act"]
    
    if event:
        base_cmd.append(event)
    
    # Handle secrets file
    if secrets_file:
        secrets_path = Path(secrets_file)
        if not secrets_path.is_absolute():
            secrets_path = cwd / secrets_file
        if not secrets_path.exists():
            error(f"Secrets file not found: {secrets_path}")
            raise typer.Exit(code=1)
        base_cmd.extend(["--secret-file", str(secrets_path)])
    elif (cwd / ".secrets").exists():
        base_cmd.extend(["--secret-file", str(cwd / ".secrets")])
        log("Using .secrets file from current directory")
    
    if dry_run:
        base_cmd.append("--dryrun")
    
    # Handle workflow_dispatch with environment input
    if event == "workflow_dispatch" and env:
        event_payload = json.dumps({"inputs": {"environment": env}})
        base_cmd.extend(["-e", event_payload])
        log(f"Using workflow_dispatch with environment: {env}")
    
    # Check if Docker is running
    try:
        docker_check = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if docker_check.returncode != 0:
            error("Docker is not running or not accessible")
            error("Please start Docker and try again")
            raise typer.Exit(code=1)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        error("Docker is not installed or not accessible")
        error("Please install Docker and ensure it's running")
        raise typer.Exit(code=1)
    
    # Ensure required Docker images are available
    if pull_images:
        if workflows_to_run:
            log("Checking for required Docker images...")
            if not ensure_required_images(workflows_to_run, cwd, progress, allow_partial=True):
                warning("⚠️  Some Docker images failed to pull, but continuing...")
                warning("⚠️  The workflow may fail if required images are missing")
        elif all_jobs and not workflows_to_run:
            # If running all jobs without specific workflows, use default image
            default_image = 'catthehacker/ubuntu:act-latest'
            if not check_docker_image_exists(default_image):
                log("Pulling default Docker image for act...")
                if not pull_docker_image(default_image, progress, max_retries=3):
                    warning("⚠️  Failed to pull default Docker image")
                    warning("⚠️  Continuing anyway - act may still work")
    else:
        log("Skipping Docker image pull (--no-pull-images)")
    
    # Calculate total tasks to run
    # If all_jobs, we run each job for each workflow
    if all_jobs and jobs_to_run:
        total_tasks = len(workflows_to_run) * len(jobs_to_run) if workflows_to_run else len(jobs_to_run)
    elif all_jobs:
        # If all_jobs but no workflows found, try to run jobs without workflow filter
        total_tasks = len(jobs_to_run)
    else:
        total_tasks = len(workflows_to_run) if workflows_to_run else 1
    
    successful = 0
    failed = 0
    console = Console()
    
    # Determine if we should show progress bars
    show_progress = progress and (total_tasks > 1 or (all_jobs and len(jobs_to_run) > 1))
    
    if show_progress:
        # Use rich progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress_bar:
            task = progress_bar.add_task(
                f"Running {total_tasks} task(s)...",
                total=total_tasks
            )
            
            # Run all jobs for all workflows
            if all_jobs and jobs_to_run:
                if workflows_to_run:
                    # Run each job for each workflow
                    for wf in workflows_to_run:
                        wf_name = Path(wf).name if wf else "workflow"
                        for job_name in jobs_to_run:
                            progress_bar.update(
                                task,
                                description=f"Running {wf_name}/{job_name} ({successful + failed + 1}/{total_tasks})"
                            )
                            
                            cmd = base_cmd.copy()
                            if wf:
                                if not Path(wf).is_absolute():
                                    wf_path = cwd / wf
                                else:
                                    wf_path = Path(wf)
                                
                                if not wf_path.exists():
                                    error(f"Workflow file not found: {wf_path}")
                                    failed += 1
                                    progress_bar.update(task, advance=1)
                                    continue
                                
                                cmd.extend(["-W", str(wf_path)])
                            
                            cmd.extend(["-j", job_name])
                            
                            result = subprocess.run(cmd, cwd=cwd)
                            
                            if result.returncode == 0:
                                successful += 1
                            else:
                                failed += 1
                            
                            progress_bar.update(task, advance=1)
                else:
                    # Run each job without workflow filter
                    for job_name in jobs_to_run:
                        progress_bar.update(
                            task,
                            description=f"Running {job_name} ({successful + failed + 1}/{total_tasks})"
                        )
                        
                        cmd = base_cmd.copy()
                        cmd.extend(["-j", job_name])
                        
                        result = subprocess.run(cmd, cwd=cwd)
                        
                        if result.returncode == 0:
                            successful += 1
                        else:
                            failed += 1
                        
                        progress_bar.update(task, advance=1)
            else:
                # Run workflows (with optional single job)
                for i, wf in enumerate(workflows_to_run):
                    wf_name = Path(wf).name if wf else "workflow"
                    progress_bar.update(task, description=f"Running {wf_name} ({i+1}/{total_tasks})")
                    
                    cmd = base_cmd.copy()
                    if wf:
                        if not Path(wf).is_absolute():
                            wf_path = cwd / wf
                        else:
                            wf_path = Path(wf)
                        
                        if not wf_path.exists():
                            error(f"Workflow file not found: {wf_path}")
                            failed += 1
                            progress_bar.update(task, advance=1)
                            continue
                        
                        cmd.extend(["-W", str(wf_path)])
                    
                    if jobs_to_run:
                        # Run each job in the workflow
                        for job_name in jobs_to_run:
                            job_cmd = cmd.copy()
                            job_cmd.extend(["-j", job_name])
                            result = subprocess.run(job_cmd, cwd=cwd)
                            if result.returncode == 0:
                                successful += 1
                            else:
                                failed += 1
                    elif job:
                        cmd.extend(["-j", job])
                        result = subprocess.run(cmd, cwd=cwd)
                        if result.returncode == 0:
                            successful += 1
                        else:
                            failed += 1
                    else:
                        # Run entire workflow
                        result = subprocess.run(cmd, cwd=cwd)
                        if result.returncode == 0:
                            successful += 1
                        else:
                            failed += 1
                    
                    progress_bar.update(task, advance=1)
    else:
        # No progress bar - run normally
        if all_jobs and jobs_to_run:
            if workflows_to_run:
                # Run each job for each workflow
                for wf in workflows_to_run:
                    wf_name = Path(wf).name if wf else "workflow"
                    for job_name in jobs_to_run:
                        log(f"Running {wf_name}/{job_name}...")
                        
                        cmd = base_cmd.copy()
                        if wf:
                            if not Path(wf).is_absolute():
                                wf_path = cwd / wf
                            else:
                                wf_path = Path(wf)
                            
                            if not wf_path.exists():
                                error(f"Workflow file not found: {wf_path}")
                                failed += 1
                                continue
                            
                            cmd.extend(["-W", str(wf_path)])
                        
                        cmd.extend(["-j", job_name])
                        
                        result = subprocess.run(cmd, cwd=cwd)
                        
                        if result.returncode == 0:
                            successful += 1
                        else:
                            failed += 1
            else:
                # Run each job without workflow filter
                for job_name in jobs_to_run:
                    log(f"Running job: {job_name}...")
                    
                    cmd = base_cmd.copy()
                    cmd.extend(["-j", job_name])
                    
                    result = subprocess.run(cmd, cwd=cwd)
                    
                    if result.returncode == 0:
                        successful += 1
                    else:
                        failed += 1
        else:
            # Run workflows (with optional single job)
            for wf in workflows_to_run:
                cmd = base_cmd.copy()
                
                if wf:
                    if not Path(wf).is_absolute():
                        wf_path = cwd / wf
                    else:
                        wf_path = Path(wf)
                    
                    if not wf_path.exists():
                        error(f"Workflow file not found: {wf_path}")
                        failed += 1
                        continue
                    
                    cmd.extend(["-W", str(wf_path)])
                
                if jobs_to_run:
                    # Run each job in the workflow
                    for job_name in jobs_to_run:
                        job_cmd = cmd.copy()
                        job_cmd.extend(["-j", job_name])
                        log(f"Running: {' '.join(job_cmd)}")
                        result = subprocess.run(job_cmd, cwd=cwd)
                        if result.returncode == 0:
                            successful += 1
                        else:
                            failed += 1
                elif job:
                    cmd.extend(["-j", job])
                    log(f"Running: {' '.join(cmd)}")
                    log("Note: This runs in Docker containers. Make sure Docker is running.")
                    result = subprocess.run(cmd, cwd=cwd)
                    if result.returncode == 0:
                        successful += 1
                    else:
                        failed += 1
                else:
                    log(f"Running: {' '.join(cmd)}")
                    log("Note: This runs in Docker containers. Make sure Docker is running.")
                    result = subprocess.run(cmd, cwd=cwd)
                    if result.returncode == 0:
                        successful += 1
                    else:
                        failed += 1
    
    # Summary
    if total_tasks > 1:
        log("")
        log("=" * 60)
        log("Test Summary:")
        log("=" * 60)
        if successful > 0:
            success(f"✅ Successful: {successful}/{total_tasks}")
        if failed > 0:
            error(f"❌ Failed: {failed}/{total_tasks}")
        log("=" * 60)
        
        if failed > 0:
            raise typer.Exit(code=1)
    else:
        if failed > 0:
            error("Test failed")
            raise typer.Exit(code=1)
        else:
            success("Test completed successfully")


@app.command()
def setup(
    provider: str = typer.Argument("github", help="CI/CD provider (github/gitlab/jenkins)"),
):
    """Set up local testing environment for CI/CD."""
    if provider == "github":
        log("Setting up GitHub Actions local testing...")
        log("")
        log("1. Install act:")
        log("   macOS:    brew install act")
        log("   Linux:    curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash")
        log("   Windows:  choco install act-cli")
        log("   Or visit: https://github.com/nektos/act")
        log("")
        log("2. Ensure Docker is running:")
        log("   docker info")
        log("")
        log("3. (Optional) Create .secrets file for any secrets:")
        log("   echo 'MY_SECRET=value' > .secrets")
        log("")
        log("4. List available workflows:")
        log("   meta cicd test --list")
        log("")
        log("5. Test a workflow:")
        log("   meta cicd test --workflow .github/workflows/meta-apply.yml")
        log("   meta cicd test --job validate")
        log("   meta cicd test --event workflow_dispatch --env dev")
        log("   meta cicd test --all-workflows  # Run all workflows")
        log("   meta cicd test --all-jobs       # Run all jobs")
        log("")
        
        # Check if act is already installed
        act_path = shutil.which("act")
        if act_path:
            success(f"✓ act is already installed at: {act_path}")
        else:
            warning("✗ act is not installed")
        
        # Check if Docker is available
        try:
            docker_check = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if docker_check.returncode == 0:
                success("✓ Docker is running")
            else:
                warning("✗ Docker is not running or not accessible")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            warning("✗ Docker is not installed or not accessible")
        
        # Check for workflows directory
        root = find_meta_repo_root()
        if root:
            workflows_dir = root / ".github" / "workflows"
        else:
            workflows_dir = Path(".github/workflows")
        
        if workflows_dir.exists():
            workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
            if workflow_files:
                success(f"✓ Found {len(workflow_files)} workflow file(s)")
            else:
                warning("✗ No workflow files found in .github/workflows")
        else:
            warning("✗ No .github/workflows directory found")
    
    elif provider == "gitlab":
        log("Setting up GitLab CI local testing...")
        log("")
        log("1. Install gitlab-runner:")
        log("   macOS:    brew install gitlab-runner")
        log("   Or visit: https://docs.gitlab.com/runner/install/")
        log("")
        log("2. Test locally:")
        log("   gitlab-runner exec docker <job-name>")
        log("")
    
    elif provider == "jenkins":
        log("Setting up Jenkins local testing...")
        log("")
        log("1. Install Jenkins:")
        log("   Visit: https://www.jenkins.io/download/")
        log("")
        log("2. Or use Jenkinsfile Runner:")
        log("   docker run --rm -v $(pwd):/workspace jenkins/jenkinsfile-runner")
        log("")
    
    else:
        error(f"Unknown provider: {provider}")
        error("Supported providers: github, gitlab, jenkins")
        raise typer.Exit(code=1)
