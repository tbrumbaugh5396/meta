# Testing Infrastructure

## Overview

This directory contains comprehensive tests for the meta-repo CLI tool using mocks and dependency injection.

## Structure

```
tests/
├── fixtures/              # Dependency injection framework
│   ├── di_container.py    # DI container for test services
│   └── mock_factories.py  # Factory functions for common mocks
├── unit/                  # Unit tests
│   ├── commands/          # Command tests
│   │   ├── test_apply.py
│   │   ├── test_validate.py
│   │   ├── test_plan.py
│   │   ├── test_lock.py
│   │   ├── test_git.py
│   │   ├── test_changeset.py
│   │   ├── test_graph.py
│   │   ├── test_install.py
│   │   ├── test_update.py
│   │   ├── test_health.py
│   │   └── test_vendor.py
│   └── utils/             # Utility tests
│       ├── test_manifest.py
│       ├── test_git_utils.py
│       ├── test_bazel.py
│       ├── test_dependencies_utils.py
│       ├── test_changeset_utils.py
│       ├── test_vendor.py
│       ├── test_secret_detection.py
│       ├── test_vendor_validation.py
│       ├── test_vendor_backup.py
│       └── test_vendor_resume.py
├── integration/           # Integration tests
└── conftest.py           # Pytest fixtures with DI support
```

## Dependency Injection Framework

### DIContainer

The `DIContainer` class provides dependency injection for tests:

```python
from .fixtures.di_container import DIContainer
# Or in conftest.py, use relative imports:
# from .fixtures.di_container import DIContainer

def test_my_function(di_container):
    git_service = di_container.get("git")
    bazel_service = di_container.get("bazel")
    # Use services...
```

### Mock Factories

Common mocks are available via factories:

- `mock_git_service()` - Git operations
- `mock_bazel_service()` - Bazel operations
- `mock_manifest_service()` - Manifest loading
- `mock_lock_service()` - Lock file operations
- `mock_dependency_service()` - Dependency resolution
- `mock_cache_service()` - Caching
- `mock_store_service()` - Content-addressed store
- `mock_health_service()` - Health checks
- `mock_changeset_service()` - Changeset operations
- `mock_vendor_service()` - Vendor operations
- `mock_secret_detection_service()` - Secret detection
- `mock_vendor_validation_service()` - Vendor validation
- `mock_vendor_backup_service()` - Backup/restore
- `mock_vendor_transaction_service()` - Atomic transactions
- `mock_vendor_network_service()` - Network resilience
- `mock_vendor_resume_service()` - Conversion resume

## Running Tests

### Run All Tests

```bash
pytest tests/
```

### Run Unit Tests Only

```bash
pytest tests/unit/
```

### Run Command Tests

```bash
pytest tests/unit/commands/
```

### Run Utility Tests

```bash
pytest tests/unit/utils/
```

### Run Specific Test File

```bash
pytest tests/unit/commands/test_apply.py
```

### Run with Coverage

```bash
pytest tests/ --cov=meta --cov-report=html
```

## Writing New Tests

### Using Dependency Injection

```python
def test_my_command(runner, temp_meta_repo, mock_git, mock_bazel):
    """Test using injected mocks."""
    with patch('meta.commands.my_module.get_components') as mock_get:
        mock_get.return_value = {"test": {}}
        result = runner.invoke(app, ["my-command"])
        assert result.exit_code == 0
```

### Using Custom Mocks

```python
def test_with_custom_mock(di_container):
    """Test with custom mock service."""
    custom_git = MagicMock()
    custom_git.checkout_version.return_value = True
    di_container.register("git", custom_git)
    
    # Use custom_git in test...
```

## Test Coverage

### Commands Tested

- ✅ `apply` - Apply changes to components
- ✅ `validate` - Validate system correctness
- ✅ `plan` - Plan changes
- ✅ `lock` - Lock file operations
- ✅ `git` - Git operations
- ✅ `changeset` - Changeset management
- ✅ `graph` - Dependency visualization
- ✅ `install` - Package installation
- ✅ `update` - Repository updates
- ✅ `health` - Health checks
- ✅ `vendor` - Vendor operations (with all enhancements)

### Utilities Tested

- ✅ `manifest` - Manifest loading
- ✅ `git` - Git utilities
- ✅ `bazel` - Bazel utilities
- ✅ `dependencies` - Dependency resolution
- ✅ `changeset` - Changeset utilities
- ✅ `vendor` - Vendor utilities
- ✅ `secret_detection` - Secret detection
- ✅ `vendor_validation` - Vendor validation
- ✅ `vendor_backup` - Backup/restore
- ✅ `vendor_resume` - Conversion resume

## Best Practices

1. **Always use mocks** - Don't make real system calls in tests
2. **Use dependency injection** - Inject services via fixtures
3. **Isolate tests** - Each test should be independent
4. **Mock external dependencies** - Git, Bazel, file system, etc.
5. **Use temp directories** - Use `temp_meta_repo` fixture for file operations
6. **Test error cases** - Test both success and failure paths

## Fixtures

### `di_container`

Provides dependency injection container with pre-registered mocks.

### `temp_meta_repo`

Creates a temporary meta-repo structure with manifests and components directories.

### `mock_git`, `mock_bazel`, etc.

Pre-configured mock services for common dependencies.

### `mock_vendor`, `mock_secret_detection`, etc.

Pre-configured mock services for vendor operations and related utilities.

## Example Test

```python
"""Example test with dependency injection."""
import pytest
from unittest.mock import patch
from typer.testing import CliRunner
from meta.cli import app


class TestMyCommand:
    """Tests for my command."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_my_command_success(self, runner, temp_meta_repo, mock_git):
        """Test successful command execution."""
        with patch('meta.commands.my_module.get_components') as mock_get:
            mock_get.return_value = {
                "test-component": {
                    "repo": "git@github.com:test/test.git",
                    "version": "v1.0.0"
                }
            }
            
            result = runner.invoke(app, ["my-command", "--env", "dev"])
            
            assert result.exit_code == 0
            mock_get.assert_called()
```

## Test Summary

### Total Test Coverage

- **Commands**: 10 command groups tested
- **Utilities**: 10+ utility modules tested
- **Vendor System**: Comprehensive coverage of all vendor features

### Vendor Test Coverage

- ✅ **Secret Detection** - 11 tests
- ✅ **Vendor Validation** - 6 tests
- ✅ **Vendor Backup** - 6 tests
- ✅ **Vendor Resume** - 7 tests
- ✅ **Vendor Commands** - 18 tests
- ✅ **Vendor Utilities** - 10 tests

**Total Vendor Tests**: 58 tests covering all critical and high-value features

## Vendor Testing

### New Vendor Features Tested

The vendor system now includes comprehensive tests for all new features:

- **Secret Detection** (`test_secret_detection.py`)
  - File scanning
  - Directory scanning
  - Component-level detection
  - Exclusion patterns

- **Vendor Validation** (`test_vendor_validation.py`)
  - Prerequisite validation
  - Component validation
  - Conversion readiness checks

- **Vendor Backup** (`test_vendor_backup.py`)
  - Backup creation
  - Backup listing
  - Backup restoration

- **Vendor Resume** (`test_vendor_resume.py`)
  - Checkpoint creation
  - Checkpoint loading
  - Conversion resumption

- **Vendor Commands** (`test_vendor.py`)
  - All new commands (verify, backup, restore, resume)
  - Enhanced convert command with all options
  - Error handling

### Example Vendor Test

```python
"""Example vendor test."""
import pytest
from unittest.mock import patch
from typer.testing import CliRunner
from meta.cli import app


class TestVendorCommand:
    """Tests for vendor commands."""
    
    def test_vendor_convert_with_dry_run(self, temp_meta_repo, mock_vendor):
        """Test convert with dry-run."""
        runner = CliRunner()
        
        with patch("meta.commands.vendor.convert_to_vendored_mode_enhanced", 
                   return_value=(True, {'dry_run': True})):
            result = runner.invoke(app, [
                "vendor", "convert", "vendored", "--dry-run"
            ])
            
            assert result.exit_code == 0
    
    def test_vendor_verify(self, temp_meta_repo, mock_vendor):
        """Test verify command."""
        runner = CliRunner()
        
        with patch("meta.commands.vendor.verify_conversion",
                   return_value=(True, {'components_valid': 1})):
            result = runner.invoke(app, ["vendor", "verify"])
            
            assert result.exit_code == 0
```

