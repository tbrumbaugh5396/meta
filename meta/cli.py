"""Main CLI entry point."""

import sys
import os

# CRITICAL: Ensure our package directory is in the path FIRST
# This prevents conflicts with other 'meta' packages installed system-wide
_setup_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _setup_dir not in sys.path:
    sys.path.insert(0, _setup_dir)

# Now we can safely import
import typer

# Import must happen after path is set
try:
    from meta.commands import (
        validate, plan, apply, test, exec as exec_cmd, lock, deps, conflicts,
        rollback, health, config, scaffold, completion, info, updates, backup,
        metrics, audit, secrets, policies, workspace, interactive, help as help_cmd,
        discover, compare, diff, publish, graph, migrate, registry, dashboard,
        plugins, analytics, git
    )
    # Phase 11-14 commands (optional, may not all be available)
    changelog = release = docs = cicd = security = None
    test_templates = license_cmd = benchmark = api = di = cost = None
    # Phase 15-18 commands
    templates = notify = alias = search_cmd = history = None
    deploy = sync = review = monitor = optimize = None
    compliance = versioning = None
    # Phase 20 commands
    os_cmd = None
    try:
        from meta.commands import changelog, release, docs, cicd, security
        from meta.commands import test_templates, license as license_cmd, benchmark, api, di, cost
        from meta.commands import templates, notify, alias, search as search_cmd, history
        from meta.commands import deploy, sync, review, monitor, optimize
        from meta.commands import compliance, versioning
        from meta.commands import os as os_cmd
    except ImportError:
        pass
    from meta.utils.logger import log, panel, set_verbose, set_debug, debug
except ImportError as e:
    # If import fails, it might be because we're still finding the wrong meta package
    # Force reload by removing the wrong one from sys.modules
    if 'meta' in sys.modules:
        del sys.modules['meta']
        if 'meta.utils' in sys.modules:
            del sys.modules['meta.utils']
        if 'meta.commands' in sys.modules:
            del sys.modules['meta.commands']
    # Try importing again
    from meta.commands import (
        validate, plan, apply, test, exec as exec_cmd, lock, deps, conflicts,
        rollback, health, config, scaffold, completion, info, updates, backup,
        metrics, audit, secrets, policies, workspace, interactive, help as help_cmd,
        discover, compare, diff, publish, graph, migrate, registry, dashboard,
        plugins, analytics, git
    )
    changelog = release = docs = cicd = security = None
    test_templates = license_cmd = benchmark = api = di = cost = None
    # Phase 15-18 commands
    templates = notify = alias = search_cmd = history = None
    deploy = sync = review = monitor = optimize = None
    compliance = versioning = None
    # Phase 20 commands
    os_cmd = None
    try:
        from meta.commands import changelog, release, docs, cicd, security
        from meta.commands import test_templates, license as license_cmd, benchmark, api, di, cost
        from meta.commands import templates, notify, alias, search as search_cmd, history
        from meta.commands import deploy, sync, review, monitor, optimize
        from meta.commands import compliance, versioning
        from meta.commands import os as os_cmd
    except ImportError:
        pass
    from meta.utils.logger import log, panel, set_verbose, set_debug, debug

app = typer.Typer(
    name="meta",
    help="Meta-repo CLI for system orchestration",
    add_completion=False
)

# Add global options for verbose/debug logging
@app.callback()
def main_callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    debug_mode: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    if debug_mode:
        set_debug(True)
        debug("Debug mode enabled.")
    elif verbose:
        set_verbose(True)
        log("Verbose mode enabled.")

    if ctx.resilient_parsing:
        return

# Add subcommands
app.add_typer(validate.app, name="validate")
app.add_typer(plan.app, name="plan")
app.add_typer(apply.app, name="apply")
app.add_typer(test.app, name="test")
app.add_typer(exec_cmd.app, name="exec")
app.add_typer(git.app, name="git")
app.add_typer(lock.app, name="lock")
app.add_typer(deps.app, name="deps")
app.add_typer(conflicts.app, name="conflicts")
app.add_typer(rollback.app, name="rollback")
app.add_typer(health.app, name="health")
app.add_typer(config.app, name="config")
app.add_typer(scaffold.app, name="scaffold")
app.add_typer(completion.app, name="completion")
app.add_typer(info.app, name="info")
app.add_typer(updates.app, name="updates")
app.add_typer(backup.app, name="backup")
app.add_typer(metrics.app, name="metrics")
app.add_typer(audit.app, name="audit")
app.add_typer(secrets.app, name="secrets")
app.add_typer(policies.app, name="policies")
app.add_typer(workspace.app, name="workspace")
app.add_typer(interactive.app, name="interactive")
app.add_typer(help_cmd.app, name="help")
app.add_typer(discover.app, name="discover")
app.add_typer(compare.app, name="compare")
app.add_typer(diff.app, name="diff")
app.add_typer(publish.app, name="publish")
app.add_typer(graph.app, name="graph")
app.add_typer(migrate.app, name="migrate")
app.add_typer(registry.app, name="registry")
app.add_typer(dashboard.app, name="dashboard")
app.add_typer(plugins.app, name="plugins")
app.add_typer(analytics.app, name="analytics")
if changelog:
    app.add_typer(changelog.app, name="changelog")
if release:
    app.add_typer(release.app, name="release")
if docs:
    app.add_typer(docs.app, name="docs")
if cicd:
    app.add_typer(cicd.app, name="cicd")
if security:
    app.add_typer(security.app, name="security")
if test_templates:
    app.add_typer(test_templates.app, name="test-templates")
if license_cmd:
    app.add_typer(license_cmd.app, name="license")
if benchmark:
    app.add_typer(benchmark.app, name="benchmark")
if api:
    app.add_typer(api.app, name="api")
if di:
    app.add_typer(di.app, name="di")
if cost:
    app.add_typer(cost.app, name="cost")
# Phase 15-18 commands
if templates:
    app.add_typer(templates.app, name="templates")
if notify:
    app.add_typer(notify.app, name="notify")
if alias:
    app.add_typer(alias.app, name="alias")
if search_cmd:
    app.add_typer(search_cmd.app, name="search")
if history:
    app.add_typer(history.app, name="history")
if deploy:
    app.add_typer(deploy.app, name="deploy")
if sync:
    app.add_typer(sync.app, name="sync")
if review:
    app.add_typer(review.app, name="review")
if monitor:
    app.add_typer(monitor.app, name="monitor")
if optimize:
    app.add_typer(optimize.app, name="optimize")
if compliance:
    app.add_typer(compliance.app, name="compliance")
if versioning:
    app.add_typer(versioning.app, name="versioning")
# Phase 20 commands
if os_cmd:
    app.add_typer(os_cmd.app, name="os")
try:
    from meta.commands import cache, store, gc
    app.add_typer(cache.app, name="cache")
    app.add_typer(store.app, name="store")
    app.add_typer(gc.app, name="gc")
except ImportError:
    pass  # Optional commands


@app.command()
def version():
    """Show meta-repo CLI version."""
    from meta import __version__
    panel(f"Meta-Repo CLI v{__version__}", "Version")


@app.command()
def status(
    env: str = typer.Option("dev", "--env", "-e", help="Environment to check"),
):
    """Show current system status."""
    log(f"System status for environment: {env}")
    
    from meta.utils.manifest import get_components, get_environment_config
    from meta.utils.git import get_current_version
    
    components = get_components()
    env_config = get_environment_config(env)
    
    from meta.utils.logger import table
    
    rows = []
    for name, comp in components.items():
        desired_version = comp.get("version", "unknown")
        current_version = get_current_version(f"components/{name}") or "not checked out"
        status = "✓" if current_version == desired_version or current_version == "not checked out" else "⚠"
        
        rows.append([
            status,
            name,
            desired_version,
            current_version,
            comp.get("type", "unknown")
        ])
    
    table(
        ["Status", "Component", "Desired Version", "Current Version", "Type"],
        rows
    )


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
