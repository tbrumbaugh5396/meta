"""Shell completion commands."""

import typer
from meta.utils.logger import log, success, error
from meta.utils.completion import install_completion, get_completion_instructions

app = typer.Typer(help="Shell completion")


@app.command()
def install(
    shell: str = typer.Argument(..., help="Shell type (bash, zsh, fish)"),
):
    """Install shell completion."""
    if shell not in ["bash", "zsh", "fish"]:
        error(f"Unsupported shell: {shell}")
        error("Supported shells: bash, zsh, fish")
        raise typer.Exit(code=1)
    
    if install_completion(shell):
        success(f"Completion installed for {shell}")
        log("\n" + get_completion_instructions(shell))
    else:
        error("Failed to install completion")
        raise typer.Exit(code=1)


