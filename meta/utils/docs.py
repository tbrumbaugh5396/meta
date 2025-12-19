"""Documentation generation utilities."""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error
from meta.utils.manifest import get_components
from meta.utils.dependencies import resolve_transitive_dependencies
from meta.utils.git import get_current_version


def generate_readme(component: str,
                    component_data: Dict[str, Any],
                    components: Dict[str, Any],
                    output_path: Optional[Path] = None) -> str:
    """Generate README for a component."""
    lines = [f"# {component}", ""]
    
    # Description
    description = component_data.get("description", f"{component} component")
    lines.append(description)
    lines.append("")
    
    # Version
    version = component_data.get("version", "unknown")
    current_version = get_current_version(f"components/{component}")
    if current_version:
        lines.append(f"**Current Version:** {current_version}")
    lines.append(f"**Manifest Version:** {version}")
    lines.append("")
    
    # Type
    comp_type = component_data.get("type", "unknown")
    lines.append(f"**Type:** {comp_type}")
    lines.append("")
    
    # Repository
    repo = component_data.get("repo", "")
    if repo:
        lines.append(f"**Repository:** {repo}")
        lines.append("")
    
    # Dependencies
    deps = resolve_transitive_dependencies(components)
    component_deps = list(deps.get(component, set()))
    if component_deps:
        lines.append("## Dependencies")
        lines.append("")
        for dep in sorted(component_deps):
            lines.append(f"- {dep}")
        lines.append("")
    
    # Build
    if comp_type == "bazel":
        build_target = component_data.get("build_target", "")
        if build_target:
            lines.append("## Building")
            lines.append("")
            lines.append(f"```bash")
            lines.append(f"bazel build {build_target}")
            lines.append(f"```")
            lines.append("")
    
    # Usage
    lines.append("## Usage")
    lines.append("")
    lines.append("See component documentation for usage instructions.")
    lines.append("")
    
    return "\n".join(lines)


def generate_api_docs(component: str,
                     component_path: Path,
                     output_path: Optional[Path] = None) -> str:
    """Generate API documentation for a component."""
    # In a real implementation, this would parse code and extract API docs
    # For now, return a placeholder
    lines = [f"# {component} API Documentation", ""]
    lines.append("API documentation generation not fully implemented.")
    lines.append("")
    lines.append("This would extract:")
    lines.append("- Function signatures")
    lines.append("- Class definitions")
    lines.append("- Type information")
    lines.append("- Documentation strings")
    lines.append("")
    
    return "\n".join(lines)


def generate_component_docs(component: str,
                           format: str = "markdown",
                           output_dir: Optional[str] = None) -> bool:
    """Generate all documentation for a component."""
    components = get_components()
    
    if component not in components:
        error(f"Component {component} not found")
        return False
    
    component_data = components[component]
    component_path = Path(f"components/{component}")
    
    if output_dir is None:
        output_dir = f"docs/{component}"
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate README
    readme = generate_readme(component, component_data, components)
    (output_path / "README.md").write_text(readme)
    success(f"Generated README for {component}")
    
    # Generate API docs
    if component_path.exists():
        api_docs = generate_api_docs(component, component_path)
        (output_path / "API.md").write_text(api_docs)
        success(f"Generated API docs for {component}")
    
    return True


