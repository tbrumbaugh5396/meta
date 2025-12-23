"""Secrets management commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error
from meta.utils.secrets import get_secrets_manager

app = typer.Typer(help="Secrets management")


@app.command()
def get(
    key: str = typer.Argument(..., help="Secret key"),
    backend: str = typer.Option("env", "--backend", help="Backend (env, vault, aws)"),
    vault_addr: Optional[str] = typer.Option(None, "--vault-addr", help="Vault address"),
    vault_token: Optional[str] = typer.Option(None, "--vault-token", help="Vault token"),
    vault_path: str = typer.Option("secret", "--vault-path", help="Vault path"),
    aws_region: Optional[str] = typer.Option(None, "--aws-region", help="AWS region"),
):
    """Get a secret value."""
    kwargs = {}
    if backend == "vault":
        kwargs["vault_addr"] = vault_addr or os.getenv("VAULT_ADDR")
        kwargs["vault_token"] = vault_token
    elif backend == "aws":
        kwargs["region"] = aws_region
    
    manager = get_secrets_manager(backend, **kwargs)
    
    if backend == "vault":
        value = manager.get(key, path=vault_path)
    else:
        value = manager.get(key)
    
    if value:
        log(value)
    else:
        error(f"Secret not found: {key}")
        raise typer.Exit(code=1)


@app.command()
def set(
    key: str = typer.Argument(..., help="Secret key"),
    value: str = typer.Argument(..., help="Secret value"),
    backend: str = typer.Option("env", "--backend", help="Backend (env, vault, aws)"),
    vault_addr: Optional[str] = typer.Option(None, "--vault-addr", help="Vault address"),
    vault_token: Optional[str] = typer.Option(None, "--vault-token", help="Vault token"),
    vault_path: str = typer.Option("secret", "--vault-path", help="Vault path"),
    aws_region: Optional[str] = typer.Option(None, "--aws-region", help="AWS region"),
):
    """Set a secret value."""
    import os
    kwargs = {}
    if backend == "vault":
        kwargs["vault_addr"] = vault_addr or os.getenv("VAULT_ADDR")
        kwargs["vault_token"] = vault_token
    elif backend == "aws":
        kwargs["region"] = aws_region
    
    manager = get_secrets_manager(backend, **kwargs)
    
    if backend == "vault":
        result = manager.set(key, value, path=vault_path)
    else:
        result = manager.set(key, value)
    
    if result:
        success(f"Secret set: {key}")
    else:
        error(f"Failed to set secret: {key}")
        raise typer.Exit(code=1)


