"""Enhanced help commands."""

import typer
from typing import Optional
from meta.utils.logger import log
from meta.utils.help_system import show_command_help, show_examples, show_interactive_help

app = typer.Typer(help="Enhanced help system")


@app.command()
def command(
    command_name: str = typer.Argument(..., help="Command name"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed help"),
):
    """Show help for a specific command."""
    show_command_help(command_name, detailed)


@app.command()
def examples():
    """Show common examples and workflows."""
    show_examples()


@app.command()
def interactive():
    """Start interactive help mode."""
    show_interactive_help()


