"""Execute commands across components."""

import typer
import subprocess
from pathlib import Path
from typing import Optional, List
from meta.utils.logger import log, success, error
from meta.utils.manifest import get_components

app = typer.Typer(help="Execute commands across components")


@app.callback(invoke_without_command=True)
def exec(
    ctx: typer.Context,
    command_parts: List[str] = typer.Argument(..., help="Command and arguments to execute"),
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Execute for specific component"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Execute for all components"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    parallel: bool = typer.Option(False, "--parallel", "-p", help="Execute in parallel"),
):
    """Run an arbitrary command across one or multiple components.
    
    Options can come before or after the command.
    
    Examples:
        meta exec pytest tests/ --component agent-core
        meta exec bazel build //... --all
        meta exec npm install --component scraper-capabilities
        meta exec --component agent-core "pytest tests/"  # Also works
    """
    # Only run if no subcommands were invoked
    if ctx.invoked_subcommand is None:
        # Parse command_parts to extract our options if they weren't already parsed
        # This allows options to come after the command (natural CLI pattern)
        actual_command_parts = []
        parsed_component = component
        parsed_all = all_components
        parsed_manifests_dir = manifests_dir
        parsed_parallel = parallel
        
        i = 0
        while i < len(command_parts):
            arg = command_parts[i]
            
            # Check for --component or -c
            if arg in ("--component", "-c"):
                if i + 1 < len(command_parts):
                    parsed_component = command_parts[i + 1]
                    i += 2  # Skip both the flag and its value
                    continue
                else:
                    error("--component requires a value")
                    raise typer.Exit(code=1)
            # Check for --all or -a
            elif arg in ("--all", "-a"):
                parsed_all = True
                i += 1
                continue
            # Check for --manifests or -m
            elif arg in ("--manifests", "-m"):
                if i + 1 < len(command_parts):
                    parsed_manifests_dir = command_parts[i + 1]
                    i += 2
                    continue
                else:
                    error("--manifests requires a value")
                    raise typer.Exit(code=1)
            # Check for --parallel or -p
            elif arg in ("--parallel", "-p"):
                parsed_parallel = True
                i += 1
                continue
            else:
                # This is part of the actual command
                actual_command_parts.append(arg)
                i += 1
        
        # Join command parts into a single command string
        command = " ".join(actual_command_parts)
        
        if not command:
            error("Command cannot be empty")
            raise typer.Exit(code=1)
        
        components = get_components(parsed_manifests_dir)
        
        # Use parsed values (from options or extracted from command_parts)
        if parsed_component:
            components_to_exec = [parsed_component]
        elif parsed_all:
            components_to_exec = list(components.keys())
        else:
            error("Must specify --component or --all")
            raise typer.Exit(code=1)
        
        results = []
        components_found = 0
        
        for comp_name in components_to_exec:
            comp_dir = Path(f"components/{comp_name}")
            if not comp_dir.exists():
                error(f"Component {comp_name} not found at {comp_dir}")
                # Add to results so we track it
                results.append({
                    "component": comp_name,
                    "success": False,
                    "error": "Component directory not found"
                })
                continue
            
            components_found += 1
            log(f"Executing '{command}' in {comp_name}")
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=comp_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    success(f"Command succeeded in {comp_name}")
                    if result.stdout:
                        log(f"Output: {result.stdout[:200]}...")  # Truncate long output
                else:
                    error(f"Command failed in {comp_name}")
                    if result.stderr:
                        error(f"Error: {result.stderr[:200]}...")
                
                results.append({
                    "component": comp_name,
                    "success": result.returncode == 0,
                    "returncode": result.returncode
                })
            except Exception as e:
                error(f"Failed to execute command in {comp_name}: {e}")
                results.append({
                    "component": comp_name,
                    "success": False,
                    "error": str(e)
                })
        
        # Summary
        if components_found == 0:
            error("No components found to execute command in")
            if parsed_component:
                error(f"Component '{parsed_component}' does not exist. Run 'meta apply --component {parsed_component}' to check it out first.")
            elif parsed_all:
                error("No components are checked out. Run 'meta apply --all' to check out all components.")
            raise typer.Exit(code=1)
        
        successful = sum(1 for r in results if r.get("success"))
        total = len(results)
        
        if successful == total:
            success(f"Command executed successfully in {successful}/{total} component(s)")
        else:
            error(f"Command failed in {total - successful}/{total} component(s)")
            raise typer.Exit(code=1)

