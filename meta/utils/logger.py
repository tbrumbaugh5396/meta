"""Unified logging for CLI operations."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional
import os

console = Console()

# Global verbosity settings
_verbose = os.getenv("META_VERBOSE", "false").lower() == "true"
_debug = os.getenv("META_DEBUG", "false").lower() == "true"


def set_verbose(enabled: bool = True):
    """Enable verbose logging."""
    global _verbose
    _verbose = enabled


def set_debug(enabled: bool = True):
    """Enable debug logging."""
    global _debug
    _debug = enabled


def is_verbose() -> bool:
    """Check if verbose mode is enabled."""
    return _verbose


def is_debug() -> bool:
    """Check if debug mode is enabled."""
    return _debug


def log(message: str, style: str = "blue", verbose: bool = False, debug: bool = False):
    """Log a message with consistent formatting."""
    if debug and not _debug:
        return
    if verbose and not _verbose:
        return
    console.print(f"[bold {style}][META][/bold {style}] {message}")


def debug(message: str):
    """Log a debug message."""
    if _debug:
        log(message, "dim", debug=True)


def success(message: str):
    """Log a success message."""
    log(message, "green")


def error(message: str):
    """Log an error message."""
    log(message, "red")


def warning(message: str):
    """Log a warning message."""
    log(message, "yellow")


def info(message: str):
    """Log an info message."""
    log(message, "cyan")


def table(headers: list, rows: list):
    """Display a table."""
    table = Table(show_header=True, header_style="bold magenta")
    for header in headers:
        table.add_column(header)
    for row in rows:
        table.add_row(*[str(cell) for cell in row])
    console.print(table)


def panel(content: str, title: Optional[str] = None):
    """Display a panel."""
    console.print(Panel(content, title=title))

