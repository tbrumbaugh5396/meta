"""Factory functions for creating common mocks."""
from unittest.mock import MagicMock, Mock
from pathlib import Path
from typing import Dict, Any


def mock_git_service() -> MagicMock:
    """Create a mock git service."""
    mock = MagicMock()
    mock.get_commit_sha_for_ref.return_value = "abc123def456"
    mock.git_available.return_value = True
    mock.checkout_version.return_value = True
    mock.pull_latest.return_value = True
    mock.get_current_version.return_value = "v1.0.0"
    mock.get_current_branch.return_value = "main"
    mock.is_dirty.return_value = False
    mock.commit.return_value = True
    mock.push.return_value = True
    mock.status.return_value = {"status": "clean"}
    return mock


def mock_bazel_service() -> MagicMock:
    """Create a mock Bazel service."""
    mock = MagicMock()
    mock.bazel_available.return_value = True
    mock.build.return_value = True
    mock.test.return_value = True
    mock.query.return_value = "//target:all"
    mock.run.return_value = (0, "Success", "")
    return mock


def mock_manifest_service() -> MagicMock:
    """Create a mock manifest service."""
    mock = MagicMock()
    mock.get_components.return_value = {
        "test-component": {
            "repo": "git@github.com:test/test.git",
            "version": "v1.0.0",
            "type": "bazel",
            "build_target": "//test:all"
        }
    }
    mock.get_environments.return_value = {
        "dev": {"test-component": "v1.0.0"},
        "staging": {"test-component": "v1.0.0"},
        "prod": {"test-component": "v1.0.0"}
    }
    mock.get_features.return_value = {
        "test-feature": {
            "components": ["test-component"],
            "description": "Test feature"
        }
    }
    mock.load_components.return_value = {}
    mock.load_environments.return_value = {}
    mock.load_features.return_value = {}
    return mock


def mock_lock_service() -> MagicMock:
    """Create a mock lock service."""
    mock = MagicMock()
    mock.generate_lock_file.return_value = True
    mock.load_lock_file.return_value = {
        "components": {
            "test-component": {
                "sha": "abc123def456",
                "version": "v1.0.0"
            }
        }
    }
    mock.validate_lock_file.return_value = True
    mock.get_locked_components.return_value = {
        "test-component": "abc123def456"
    }
    return mock


def mock_dependency_service() -> MagicMock:
    """Create a mock dependency service."""
    mock = MagicMock()
    mock.resolve_dependencies.return_value = {
        "test-component": {"dep1", "dep2"}
    }
    mock.validate_dependencies.return_value = True
    mock.detect_conflicts.return_value = []
    mock.get_dependency_graph.return_value = {
        "test-component": ["dep1", "dep2"]
    }
    return mock


def mock_cache_service() -> MagicMock:
    """Create a mock cache service."""
    mock = MagicMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.clear.return_value = True
    mock.exists.return_value = False
    return mock


def mock_store_service() -> MagicMock:
    """Create a mock store service."""
    mock = MagicMock()
    mock.add.return_value = "hash123"
    mock.get.return_value = b"content"
    mock.exists.return_value = False
    mock.list.return_value = []
    return mock


def mock_health_service() -> MagicMock:
    """Create a mock health service."""
    mock = MagicMock()
    mock.check_component_health.return_value = {
        "healthy": True,
        "status": "ok"
    }
    mock.check_system_health.return_value = {
        "all_healthy": True,
        "components": {}
    }
    return mock


def mock_changeset_service() -> MagicMock:
    """Create a mock changeset service."""
    mock = MagicMock()
    mock.create_changeset.return_value = "changeset-123"
    mock.load_changeset.return_value = {
        "id": "changeset-123",
        "description": "Test changeset",
        "status": "in_progress"
    }
    mock.list_changesets.return_value = []
    mock.finalize_changeset.return_value = True
    mock.rollback_changeset.return_value = True
    return mock


def mock_vendor_service() -> MagicMock:
    """Create a mock vendor service."""
    mock = MagicMock()
    mock.is_vendored_mode.return_value = False
    mock.vendor_component.return_value = True
    mock.get_vendor_info.return_value = {
        "component": "test-component",
        "repo": "git@github.com:test/test.git",
        "version": "v1.0.0",
        "vendored_at": "2024-01-15T10:30:00Z"
    }
    mock.is_component_vendored.return_value = False
    mock.convert_to_vendored_mode.return_value = True
    mock.convert_to_reference_mode.return_value = True
    mock.convert_to_vendored_for_production.return_value = True
    return mock


def mock_file_system(tmp_path: Path) -> Dict[str, Path]:
    """Create a mock file system structure."""
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    (manifests / "components.yaml").write_text("components: {}")
    (manifests / "environments.yaml").write_text("environments:\n  dev: {}")
    (manifests / "features.yaml").write_text("features: {}")
    
    components = tmp_path / "components"
    components.mkdir()
    
    return {
        "root": tmp_path,
        "manifests": manifests,
        "components": components
    }


