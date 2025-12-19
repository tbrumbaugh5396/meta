"""Interactive mode utilities."""

from typing import List, Optional, Dict, Any, Callable
from meta.utils.logger import log, success, error
from meta.utils.manifest import get_components
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def select_component(components: Optional[List[str]] = None,
                    manifests_dir: str = "manifests") -> Optional[str]:
    """Interactive component selection."""
    if components is None:
        components = list(get_components(manifests_dir).keys())
    
    if not components:
        error("No components available")
        return None
    
    console.print("\n[bold]Select Component:[/bold]")
    table = Table(show_header=False)
    for i, comp in enumerate(components, 1):
        table.add_row(f"{i}.", comp)
    console.print(table)
    
    while True:
        choice = Prompt.ask("Enter component number or name", default="")
        if not choice:
            return None
        
        # Try number first
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(components):
                return components[idx]
        except ValueError:
            pass
        
        # Try name
        if choice in components:
            return choice
        
        error(f"Invalid choice: {choice}")


def select_environment(default: str = "dev") -> str:
    """Interactive environment selection."""
    environments = ["dev", "staging", "prod"]
    
    console.print("\n[bold]Select Environment:[/bold]")
    for i, env in enumerate(environments, 1):
        marker = " (default)" if env == default else ""
        console.print(f"{i}. {env}{marker}")
    
    choice = Prompt.ask("Enter environment", default=default)
    return choice if choice in environments else default


def confirm_action(message: str, default: bool = False) -> bool:
    """Confirm an action."""
    return Confirm.ask(message, default=default)


def select_from_list(items: List[str], prompt: str = "Select item") -> Optional[str]:
    """Select from a list of items."""
    if not items:
        return None
    
    console.print(f"\n[bold]{prompt}:[/bold]")
    table = Table(show_header=False)
    for i, item in enumerate(items, 1):
        table.add_row(f"{i}.", item)
    console.print(table)
    
    while True:
        choice = Prompt.ask("Enter number or name", default="")
        if not choice:
            return None
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return items[idx]
        except ValueError:
            pass
        
        if choice in items:
            return choice
        
        error(f"Invalid choice: {choice}")


def show_menu(title: str, options: List[Dict[str, Any]]) -> Optional[str]:
    """Show interactive menu."""
    console.print(f"\n[bold]{title}[/bold]")
    table = Table(show_header=False)
    for i, option in enumerate(options, 1):
        table.add_row(f"{i}.", option.get("label", option.get("name", "")))
    console.print(table)
    
    choice = Prompt.ask("Select option", default="")
    if not choice:
        return None
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(options):
            return options[idx].get("action") or options[idx].get("name")
    except ValueError:
        pass
    
    return None


def interactive_workflow(workflow_name: str, steps: List[Callable]) -> Any:
    """Run an interactive workflow."""
    console.print(Panel(f"Starting workflow: {workflow_name}", title="Workflow"))
    
    result = None
    for i, step in enumerate(steps, 1):
        console.print(f"\n[bold]Step {i}/{len(steps)}[/bold]")
        try:
            result = step(result)
            if result is False:  # User cancelled
                return None
        except KeyboardInterrupt:
            console.print("\n[red]Cancelled by user[/red]")
            return None
        except Exception as e:
            error(f"Error in step {i}: {e}")
            if not confirm_action("Continue anyway?", default=False):
                return None
    
    success(f"Workflow '{workflow_name}' completed!")
    return result


