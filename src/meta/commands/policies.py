"""Policy enforcement commands."""

import typer
from typing import Optional
from meta.utils.logger import log, success, error, table, panel
from meta.utils.policies import get_policy_engine
from meta.utils.manifest import get_components
from meta.utils.dependencies import resolve_transitive_dependencies

app = typer.Typer(help="Policy enforcement")


@app.command()
def check(
    component: Optional[str] = typer.Option(None, "--component", "-c", help="Check specific component"),
    manifests_dir: str = typer.Option("manifests", "--manifests", "-m", help="Manifests directory"),
):
    """Check if components comply with policies."""
    engine = get_policy_engine()
    components = get_components(manifests_dir)
    deps = resolve_transitive_dependencies(components)
    
    if component:
        if component not in components:
            error(f"Component {component} not found")
            raise typer.Exit(code=1)
        
        comp_data = components[component]
        version = comp_data.get("version", "latest")
        component_deps = list(deps.get(component, set()))
        
        valid, errors = engine.validate_apply(component, version, component_deps)
        
        if valid:
            success(f"{component} complies with policies")
        else:
            error(f"{component} violates policies:")
            for err in errors:
                error(f"  - {err}")
            raise typer.Exit(code=1)
    else:
        # Check all components
        all_valid = True
        rows = []
        
        for comp_name, comp_data in components.items():
            version = comp_data.get("version", "latest")
            component_deps = list(deps.get(comp_name, set()))
            
            valid, errors = engine.validate_apply(comp_name, version, component_deps)
            status = "✅" if valid else "❌"
            rows.append([status, comp_name, len(errors)])
            
            if not valid:
                all_valid = False
        
        panel("Policy Compliance", "Policies")
        table(["Status", "Component", "Violations"], rows)
        
        if not all_valid:
            error("Some components violate policies")
            raise typer.Exit(code=1)
        else:
            success("All components comply with policies")


