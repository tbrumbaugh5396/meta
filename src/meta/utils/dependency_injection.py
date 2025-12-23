"""Dependency injection utilities."""

from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error
from meta.utils.manifest import get_components
from meta.utils.dependencies import resolve_transitive_dependencies


def discover_services(component: str,
                     component_path: Path) -> List[Dict[str, Any]]:
    """Discover services in a component."""
    # In a real implementation, this would scan for service definitions
    # For now, return empty list
    return []


def inject_dependency(component: str,
                     dependency: str,
                     component_path: Path) -> bool:
    """Inject a dependency into a component."""
    # In a real implementation, this would modify component configuration
    # to inject the dependency
    log(f"Injecting {dependency} into {component}")
    return True


def validate_dependencies(component: str,
                         component_path: Path) -> bool:
    """Validate component dependencies."""
    components = get_components()
    deps = resolve_transitive_dependencies(components)
    component_deps = deps.get(component, set())
    
    # Check if all dependencies are available
    for dep in component_deps:
        dep_path = Path(f"components/{dep}")
        if not dep_path.exists():
            error(f"Dependency {dep} not found")
            return False
    
    return True


