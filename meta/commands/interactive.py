"""Interactive mode commands."""

import typer
import sys
from meta.utils.logger import log, success, error
from meta.utils.interactive import (
    select_component, select_environment, confirm_action,
    show_menu, interactive_workflow
)
from meta.utils.manifest import get_components

app = typer.Typer(help="Interactive mode")


class MockContext:
    """Mock Typer context for calling commands programmatically."""
    def __init__(self):
        self.invoked_subcommand = None
        self.resilient_parsing = False


@app.callback(invoke_without_command=True)
def interactive(
    ctx: typer.Context,
):
    """Start interactive mode."""
    if ctx.invoked_subcommand is None:
        log("Starting interactive mode...")
        
        # Main menu
        options = [
            {"label": "Apply components", "action": "apply"},
            {"label": "Check health", "action": "health"},
            {"label": "Plan changes", "action": "plan"},
            {"label": "Validate system", "action": "validate"},
            {"label": "Show status", "action": "status"},
            {"label": "Exit", "action": "exit"},
        ]
        
        while True:
            choice = show_menu("Meta-Repo CLI - Main Menu", options)
            
            if not choice or choice == "exit":
                log("Exiting interactive mode")
                break
            
            if choice == "apply":
                _interactive_apply()
            elif choice == "health":
                _interactive_health()
            elif choice == "plan":
                _interactive_plan()
            elif choice == "validate":
                _interactive_validate()
            elif choice == "status":
                _interactive_status()


def _interactive_apply():
    """Interactive apply workflow."""
    from meta.utils.interactive import select_component, select_environment, confirm_action
    from meta.commands.apply import apply
    
    env = select_environment()
    component = select_component()
    
    if not component:
        return
    
    if confirm_action(f"Apply {component} to {env}?", default=True):
        log(f"Applying {component} to {env}...")
        try:
            ctx = MockContext()
            apply(ctx, env=env, component=component)
        except SystemExit as e:
            # Command may exit with non-zero code, that's okay
            if e.code != 0:
                pass
        except Exception as e:
            error(f"Failed to apply {component}: {e}")


def _interactive_health():
    """Interactive health check."""
    from meta.utils.interactive import select_component, select_environment
    from meta.commands.health import health
    
    env = select_environment()
    component = select_component()
    
    try:
        ctx = MockContext()
        if component:
            log(f"Checking health of {component}...")
            health(ctx, component=component, env=env)
        else:
            log("Checking health of all components...")
            health(ctx, all=True, env=env)
    except SystemExit as e:
        # Health command may exit with code 1 if unhealthy, that's expected
        if e.code != 0:
            pass
    except Exception as e:
        error(f"Failed to check health: {e}")


def _interactive_plan():
    """Interactive plan."""
    from meta.utils.interactive import select_environment
    from meta.commands.plan import plan
    
    env = select_environment()
    log(f"Planning changes for {env}...")
    try:
        ctx = MockContext()
        plan(ctx, env=env)
    except SystemExit as e:
        if e.code != 0:
            pass
    except Exception as e:
        error(f"Failed to plan: {e}")


def _interactive_validate():
    """Interactive validate."""
    from meta.utils.interactive import select_environment
    from meta.commands.validate import validate
    
    env = select_environment()
    log(f"Validating {env}...")
    try:
        ctx = MockContext()
        validate(ctx, env=env)
    except SystemExit as e:
        # Validate may exit with code 1 if validation fails, that's expected
        if e.code != 0:
            pass
    except Exception as e:
        error(f"Failed to validate: {e}")


def _interactive_status():
    """Interactive status."""
    from meta.utils.interactive import select_environment
    from meta.cli import status
    
    env = select_environment()
    log("Showing system status...")
    try:
        status(env=env)
    except Exception as e:
        error(f"Failed to show status: {e}")


