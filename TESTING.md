# Testing Guide for Meta-Repo CLI

## Overview

The meta-repo CLI includes comprehensive unit and integration tests to ensure reliability and correctness.

## Test Structure

```
tests/
├── unit/                    # Unit tests for utilities
│   ├── test_lock.py        # Lock file utilities
│   ├── test_dependencies.py # Dependency resolution
│   └── test_packages.py    # Package manager utilities
├── integration/             # Integration tests
│   ├── test_lock_command.py      # Lock command end-to-end
│   └── test_dependency_validation.py  # Dependency validation
└── conftest.py             # Pytest fixtures
```

## Running Tests

### Run All Tests

```bash
pytest tests/
```

### Run Unit Tests Only

```bash
pytest tests/unit/
```

### Run Integration Tests Only

```bash
pytest tests/integration/
```

### Run Specific Test File

```bash
pytest tests/unit/test_lock.py
```

### Run with Verbose Output

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=meta --cov-report=html
```

## Test Categories

### Unit Tests

Unit tests test individual utilities in isolation:

- **`test_lock.py`** - Tests lock file generation, loading, and validation
- **`test_dependencies.py`** - Tests dependency resolution and validation
- **`test_packages.py`** - Tests package manager detection and installation

### Integration Tests

Integration tests test the full CLI workflow:

- **`test_lock_command.py`** - Tests `meta lock` command end-to-end
- **`test_dependency_validation.py`** - Tests dependency validation in `meta validate`

## Writing New Tests

### Unit Test Example

```python
def test_my_function():
    """Test description."""
    result = my_function("input")
    assert result == "expected_output"
```

### Integration Test Example

```python
from typer.testing import CliRunner
from meta.cli import app

def test_my_command():
    """Test CLI command."""
    runner = CliRunner()
    result = runner.invoke(app, ["my-command", "--option", "value"])
    assert result.exit_code == 0
```

## Test Fixtures

The `conftest.py` provides common fixtures:

- **`temp_manifests`** - Creates a temporary manifests directory with basic structure

## Continuous Integration

Tests should be run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest tests/
```

## Coverage Goals

- **Unit Tests**: > 80% coverage for utilities
- **Integration Tests**: Cover all major CLI workflows
- **Edge Cases**: Test error conditions and boundary cases

## Best Practices

1. **Test isolation** - Each test should be independent
2. **Mock external dependencies** - Use mocks for Git, file system, etc.
3. **Test error cases** - Don't just test happy paths
4. **Clear test names** - Test names should describe what they test
5. **Fast tests** - Unit tests should run quickly (< 1 second each)

## Debugging Tests

### Run with Print Statements

```bash
pytest tests/ -s
```

### Run Specific Test

```bash
pytest tests/unit/test_lock.py::TestLockFileGeneration::test_generate_lock_file_creates_file
```

### Run with PDB Debugger

```bash
pytest tests/ --pdb
```

## Phase 15-20 Tests

### Unit Tests Added

- **`test_templates_library.py`** - Tests for component templates library
- **`test_aliases.py`** - Tests for component aliases
- **`test_search.py`** - Tests for enhanced component search
- **`test_deployment.py`** - Tests for deployment strategies
- **`test_sync.py`** - Tests for component synchronization
- **`test_compliance.py`** - Tests for compliance reporting
- **`test_os_config.py`** - Tests for OS configuration manifests

### Integration Tests Added

- **`test_phase15_20_commands.py`** - Integration tests for Phase 15-20 commands

## Next Steps

- Add more integration tests for `meta apply` with lock files
- Add tests for package manager installation
- Add performance tests for large dependency graphs
- Add tests for error recovery and rollback
- Add tests for OS provisioning and deployment

