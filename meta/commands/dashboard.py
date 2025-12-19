"""Component dashboard commands."""

import typer
from typing import Optional
from meta.utils.logger import log
from meta.utils.dashboard import generate_dashboard, display_dashboard

app = typer.Typer(help="Component dashboard")


@app.callback(invoke_without_command=True)
def dashboard(
    ctx: typer.Context,
    env: Optional[str] = typer.Option(None, "--env", "-e", help="Environment"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    web: bool = typer.Option(False, "--web", help="Start web server"),
    port: int = typer.Option(8080, "--port", "-p", help="Web server port"),
):
    """Show component dashboard."""
    if ctx.invoked_subcommand is None:
        if web:
            log("Starting web dashboard...")
            # In a real implementation, start a web server
            log(f"Web dashboard would start on http://localhost:{port}")
            log("Web UI not fully implemented - use a web framework like Flask/FastAPI")
        else:
            dashboard_data = generate_dashboard(env, manifests_dir)
            display_dashboard(dashboard_data)


