"""Component versioning strategies utilities."""

from typing import Dict, Any, List, Optional, Literal
from meta.utils.logger import log, success, error
from meta.utils.manifest import get_components, update_component_version_in_manifest
from meta.utils.version import compare_versions
from meta.utils.git import get_latest_remote_version, tag_version


VersioningStrategy = Literal["semantic", "calendar", "snapshot", "custom"]


class VersioningStrategyManager:
    """Manages versioning strategies."""
    
    def apply_strategy(
        self,
        component: str,
        strategy: VersioningStrategy,
        current_version: Optional[str] = None,
        manifests_dir: str = "manifests"
    ) -> Optional[str]:
        """Apply versioning strategy to generate new version."""
        if strategy == "semantic":
            return self._semantic_versioning(component, current_version, manifests_dir)
        elif strategy == "calendar":
            return self._calendar_versioning(component, manifests_dir)
        elif strategy == "snapshot":
            return self._snapshot_versioning(component, manifests_dir)
        elif strategy == "custom":
            return self._custom_versioning(component, manifests_dir)
        else:
            error(f"Unknown versioning strategy: {strategy}")
            return None
    
    def _semantic_versioning(
        self,
        component: str,
        current_version: Optional[str],
        manifests_dir: str
    ) -> Optional[str]:
        """Semantic versioning (major.minor.patch)."""
        if not current_version:
            current_version = "0.0.0"
        
        # Parse version
        parts = current_version.split(".")
        if len(parts) != 3:
            error(f"Invalid semantic version: {current_version}")
            return None
        
        try:
            major, minor, patch = map(int, parts)
        except ValueError:
            error(f"Invalid semantic version: {current_version}")
            return None
        
        # Increment patch by default
        new_version = f"{major}.{minor}.{patch + 1}"
        return new_version
    
    def _calendar_versioning(
        self,
        component: str,
        manifests_dir: str
    ) -> Optional[str]:
        """Calendar versioning (YYYY.MM.DD)."""
        from datetime import datetime
        now = datetime.now()
        return f"{now.year}.{now.month:02d}.{now.day:02d}"
    
    def _snapshot_versioning(
        self,
        component: str,
        manifests_dir: str
    ) -> Optional[str]:
        """Snapshot versioning (commit SHA)."""
        from meta.utils.git import get_commit_sha
        sha = get_commit_sha(f"components/{component}")
        if sha:
            return f"snapshot-{sha[:8]}"
        return "snapshot-latest"
    
    def _custom_versioning(
        self,
        component: str,
        manifests_dir: str
    ) -> Optional[str]:
        """Custom versioning (from component config)."""
        components = get_components(manifests_dir)
        comp = components.get(component, {})
        
        version_template = comp.get("version_template", "{major}.{minor}.{patch}")
        # In a real implementation, parse and apply template
        return "custom-1.0.0"
    
    def bump_version(
        self,
        component: str,
        level: str = "patch",
        strategy: VersioningStrategy = "semantic",
        manifests_dir: str = "manifests"
    ) -> bool:
        """Bump component version."""
        components = get_components(manifests_dir)
        comp = components.get(component)
        
        if not comp:
            error(f"Component {component} not found")
            return False
        
        current_version = comp.get("version")
        new_version = self.apply_strategy(component, strategy, current_version, manifests_dir)
        
        if not new_version:
            return False
        
        # Update manifest
        if update_component_version_in_manifest(component, new_version, manifests_dir):
            success(f"Bumped {component} from {current_version} to {new_version}")
            return True
        else:
            error("Failed to update version")
            return False


def get_versioning_manager() -> VersioningStrategyManager:
    """Get versioning strategy manager."""
    return VersioningStrategyManager()


