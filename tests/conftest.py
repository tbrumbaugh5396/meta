"""Pytest configuration and fixtures."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from .fixtures.di_container import DIContainer
from .fixtures.mock_factories import (
    mock_git_service,
    mock_bazel_service,
    mock_manifest_service,
    mock_lock_service,
    mock_dependency_service,
    mock_cache_service,
    mock_store_service,
    mock_health_service,
    mock_changeset_service,
    mock_vendor_service,
    mock_secret_detection_service,
    mock_vendor_validation_service,
    mock_vendor_backup_service,
    mock_vendor_transaction_service,
    mock_vendor_network_service,
    mock_vendor_resume_service,
    mock_file_system
)


@pytest.fixture
def di_container():
    """Dependency injection container."""
    container = DIContainer()
    # Register default mocks
    container.register("git", mock_git_service())
    container.register("bazel", mock_bazel_service())
    container.register("manifest", mock_manifest_service())
    container.register("lock", mock_lock_service())
    container.register("dependencies", mock_dependency_service())
    container.register("cache", mock_cache_service())
    container.register("store", mock_store_service())
    container.register("health", mock_health_service())
    container.register("changeset", mock_changeset_service())
    container.register("vendor", mock_vendor_service())
    container.register("secret_detection", mock_secret_detection_service())
    container.register("vendor_validation", mock_vendor_validation_service())
    container.register("vendor_backup", mock_vendor_backup_service())
    container.register("vendor_transaction", mock_vendor_transaction_service())
    container.register("vendor_network", mock_vendor_network_service())
    container.register("vendor_resume", mock_vendor_resume_service())
    return container


@pytest.fixture
def temp_meta_repo(di_container):
    """Create a temporary meta-repo structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        file_system = mock_file_system(repo_path)
        
        yield {
            "path": repo_path,
            "manifests": file_system["manifests"],
            "components": file_system["components"],
            "di": di_container
        }


@pytest.fixture
def temp_manifests():
    """Create a temporary manifests directory with basic structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manifests_dir = Path(tmpdir) / "manifests"
        manifests_dir.mkdir()
        
        # Create basic components.yaml
        components_yaml = manifests_dir / "components.yaml"
        components_yaml.write_text("""
components: {}
""")
        
        # Create basic environments.yaml
        env_yaml = manifests_dir / "environments.yaml"
        env_yaml.write_text("""
environments:
  dev: {}
""")
        
        # Create basic features.yaml
        features_yaml = manifests_dir / "features.yaml"
        features_yaml.write_text("""
features: {}
""")
        
        yield str(manifests_dir)


@pytest.fixture
def mock_git(di_container):
    """Provide a mocked git service."""
    return di_container.get("git")


@pytest.fixture
def mock_bazel(di_container):
    """Provide a mocked bazel service."""
    return di_container.get("bazel")


@pytest.fixture
def mock_manifest(di_container):
    """Provide a mocked manifest service."""
    return di_container.get("manifest")


@pytest.fixture
def mock_lock(di_container):
    """Provide a mocked lock service."""
    return di_container.get("lock")


@pytest.fixture
def mock_dependencies(di_container):
    """Provide a mocked dependency service."""
    return di_container.get("dependencies")


@pytest.fixture
def mock_cache(di_container):
    """Provide a mocked cache service."""
    return di_container.get("cache")


@pytest.fixture
def mock_store(di_container):
    """Provide a mocked store service."""
    return di_container.get("store")


@pytest.fixture
def mock_health(di_container):
    """Provide a mocked health service."""
    return di_container.get("health")


@pytest.fixture
def mock_changeset(di_container):
    """Provide a mocked changeset service."""
    return di_container.get("changeset")


@pytest.fixture
def mock_vendor(di_container):
    """Provide a mocked vendor service."""
    return di_container.get("vendor")


@pytest.fixture
def mock_secret_detection(di_container):
    """Provide a mocked secret detection service."""
    return di_container.get("secret_detection")


@pytest.fixture
def mock_vendor_validation(di_container):
    """Provide a mocked vendor validation service."""
    return di_container.get("vendor_validation")


@pytest.fixture
def mock_vendor_backup(di_container):
    """Provide a mocked vendor backup service."""
    return di_container.get("vendor_backup")


@pytest.fixture
def mock_vendor_transaction(di_container):
    """Provide a mocked vendor transaction service."""
    return di_container.get("vendor_transaction")


@pytest.fixture
def mock_vendor_network(di_container):
    """Provide a mocked vendor network service."""
    return di_container.get("vendor_network")


@pytest.fixture
def mock_vendor_resume(di_container):
    """Provide a mocked vendor resume service."""
    return di_container.get("vendor_resume")


