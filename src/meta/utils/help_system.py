"""Enhanced help system."""

from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

console = Console()

COMMAND_EXAMPLES = {
    "validate": """
**Examples:**
```bash
# Validate dev environment
meta validate --env dev

# Validate staging, skip Bazel checks
meta validate --env staging --skip-bazel

# Quick validation
meta validate --skip-git --skip-bazel
```
""",
    "apply": """
**Examples:**
```bash
# Apply all changes to staging
meta apply --env staging

# Apply specific component
meta apply --component scraper-capabilities --env prod

# Apply with lock file (production)
meta apply --env prod --locked

# Apply in parallel with progress
meta apply --all --parallel --jobs 4 --progress

# Apply with error recovery
meta apply --all --continue-on-error --retry 3
```
""",
    "plan": """
**Examples:**
```bash
# Plan changes for staging
meta plan --env staging

# Plan for specific component
meta plan --component agent-core --env prod
```
""",
    "health": """
**Examples:**
```bash
# Check health of all components
meta health --all

# Check specific component
meta health --component scraper-capabilities

# Include build and test checks
meta health --all --build --tests
```
""",
    "rollback": """
**Examples:**
```bash
# Rollback component to version
meta rollback component scraper-capabilities --to-version v2.0.0

# Rollback from lock file
meta rollback lock manifests/components.lock.prod.yaml

# List available rollback targets
meta rollback list
```
""",
}


def show_command_help(command: str, detailed: bool = False):
    """Show help for a specific command."""
    examples = COMMAND_EXAMPLES.get(command, "No examples available.")
    
    console.print(Panel(f"[bold]Command:[/bold] meta {command}", title="Help"))
    console.print(Markdown(examples))
    
    if detailed:
        # Show full command help
        import subprocess
        try:
            result = subprocess.run(
                ["meta", command, "--help"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                console.print("\n[bold]Full Help:[/bold]")
                console.print(result.stdout)
        except:
            pass


def show_examples():
    """Show common examples."""
    console.print(Panel("Common Workflows", title="Examples"))
    
    workflows = [
        {
            "name": "Daily Development",
            "commands": [
                "meta status --env dev",
                "meta validate --env dev",
                "meta apply --env dev --component my-component",
                "meta health --component my-component"
            ]
        },
        {
            "name": "Deploy to Staging",
            "commands": [
                "meta validate --env staging",
                "meta plan --env staging",
                "meta lock --env staging",
                "meta apply --env staging --locked",
                "meta health --all --env staging"
            ]
        },
        {
            "name": "Production Deployment",
            "commands": [
                "meta validate --env prod",
                "meta plan --env prod",
                "meta lock --env prod",
                "meta apply --env prod --locked --parallel",
                "meta health --all --env prod --build --tests"
            ]
        },
        {
            "name": "Component Update",
            "commands": [
                "meta updates check --component my-component",
                "meta updates update --component my-component",
                "meta validate --env dev",
                "meta apply --env dev"
            ]
        },
        {
            "name": "Emergency Rollback",
            "commands": [
                "meta rollback list",
                "meta rollback component my-component --to-version v1.0.0",
                "meta health --all"
            ]
        }
    ]
    
    for workflow in workflows:
        console.print(f"\n[bold]{workflow['name']}:[/bold]")
        for cmd in workflow["commands"]:
            console.print(f"  {cmd}")


def show_interactive_help():
    """Show interactive help."""
    console.print(Panel("Interactive Help Mode", title="Help"))
    
    options = [
        "1. Show command examples",
        "2. Show common workflows",
        "3. Show command help",
        "4. Exit"
    ]
    
    for option in options:
        console.print(option)
    
    from meta.utils.interactive import Prompt
    choice = Prompt.ask("\nSelect option", default="4")
    
    if choice == "1":
        show_examples()
    elif choice == "2":
        show_examples()
    elif choice == "3":
        command = Prompt.ask("Enter command name", default="apply")
        show_command_help(command, detailed=True)


