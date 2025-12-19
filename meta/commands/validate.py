"""Validate system correctness."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table
from meta.utils.manifest import get_components, get_features, get_environment_config
from meta.utils.version import check_versions
from meta.utils.bazel import check_bazel_target_exists, bazel_available
from meta.utils.git import git_available
from meta.utils.dependencies import validate_dependencies as validate_component_dependencies

app = typer.Typer(help="Validate system correctness")


def validate_components(env: str, manifests_dir: str = "manifests") -> bool:
    """Validate all components."""
    log("Validating component versions...")
    components = get_components(manifests_dir)
    env_config = get_environment_config(env, manifests_dir)
    
    all_valid = True
    rows = []
    
    for name, comp in components.items():
        version = comp.get("version", "unknown")
        comp_env = env_config.get(name, env)
        
        # Check version format
        version_valid = check_versions(name, version)
        
        # Check if component type is supported
        comp_type = comp.get("type", "unknown")
        type_valid = comp_type in ["bazel", "docker", "python", "npm"]
        
        # Check Bazel target if applicable
        bazel_valid = True
        if comp_type == "bazel":
            if bazel_available():
                build_target = comp.get("build_target", "")
                if build_target:
                    bazel_valid = check_bazel_target_exists(build_target)
            else:
                log(f"Bazel not available, skipping Bazel target check for {name}")
                bazel_valid = True  # Don't fail if Bazel isn't available
        
        valid = version_valid and type_valid and bazel_valid
        all_valid = all_valid and valid
        
        status = "✓" if valid else "✗"
        rows.append([
            status,
            name,
            version,
            comp_type,
            comp_env,
            "✓" if bazel_valid else "✗"
        ])
    
    table(
        ["Status", "Component", "Version", "Type", "Environment", "Bazel Target"],
        rows
    )
    
    return all_valid


def validate_features(manifests_dir: str = "manifests") -> bool:
    """Validate feature contracts."""
    log("Validating feature contracts...")
    features = get_features(manifests_dir)
    components = get_components(manifests_dir)
    
    all_valid = True
    
    for feature_name, feature_data in features.items():
        log(f"Checking feature: {feature_name}")
        
        # Check that all referenced components exist
        feature_components = feature_data.get("components", [])
        for comp_name in feature_components:
            if comp_name not in components:
                error(f"Feature {feature_name} references unknown component: {comp_name}")
                all_valid = False
        
        # Check contracts (simplified - can be extended)
        contracts = feature_data.get("contracts", [])
        for contract in contracts:
            log(f"  Contract: {contract}")
            # TODO: Implement actual contract validation logic
    
    return all_valid


def validate_dependencies(manifests_dir: str = "manifests") -> bool:
    """Validate dependency graph is acyclic."""
    log("Validating dependency graph...")
    
    # Validate component dependencies
    comp_valid, comp_errors = validate_component_dependencies(manifests_dir)
    if not comp_valid:
        return False
    
    # Also validate feature dependencies (existing logic)
    features = get_features(manifests_dir)
    
    # Build dependency graph
    graph = {}
    for feature_name, feature_data in features.items():
        graph[feature_name] = feature_data.get("depends_on", [])
    
    # Check for cycles (simplified DFS)
    visited = set()
    rec_stack = set()
    
    def has_cycle(node):
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(node)
        return False
    
    for node in graph:
        if node not in visited:
            if has_cycle(node):
                error(f"Circular dependency detected involving: {node}")
                return False
    
    return True


@app.callback(invoke_without_command=True)
def validate(
    ctx: typer.Context,
    env: str = typer.Option("dev", "--env", "-e", help="Environment to validate"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
    skip_bazel: bool = typer.Option(False, "--skip-bazel", help="Skip Bazel validation"),
    skip_git: bool = typer.Option(False, "--skip-git", help="Skip Git validation"),
):
    """Validate system correctness."""
    # Only run if no subcommands were invoked
    if ctx.invoked_subcommand is None:
        log(f"Validating system for environment: {env}")
        
        # Check prerequisites
        if not skip_bazel and not bazel_available():
            error("Bazel is not available. Use --skip-bazel to continue without Bazel validation.")
            raise typer.Exit(code=1)
        
        if not skip_git and not git_available():
            error("Git is not available. Use --skip-git to continue without Git validation.")
            raise typer.Exit(code=1)
        
        all_valid = True
        
        # Validate components
        if not validate_components(env, manifests_dir):
            all_valid = False
        
        # Validate features
        if not validate_features(manifests_dir):
            all_valid = False
        
        # Validate dependencies
        if not validate_dependencies(manifests_dir):
            all_valid = False
        
        if all_valid:
            success("All validations passed!")
            raise typer.Exit(code=0)
        else:
            error("Validation failed!")
            raise typer.Exit(code=1)

