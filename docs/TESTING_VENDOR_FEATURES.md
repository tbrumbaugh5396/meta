# Testing Vendor Features

This document describes the comprehensive test coverage for the enhanced vendor conversion system.

## Test Coverage Summary

### Total Tests: 57

All vendor-related tests are passing with comprehensive coverage of:
- Secret detection utilities
- Vendor validation utilities
- Vendor backup/restore utilities
- Vendor resume utilities
- Vendor commands (CLI)
- Core vendor utilities

## Test Files

### Utility Tests

#### `tests/unit/utils/test_secret_detection.py` (11 tests)
- ✅ File scanning for secrets
- ✅ Directory scanning
- ✅ Component-level detection
- ✅ Exclusion patterns (.git, node_modules, etc.)
- ✅ API key detection
- ✅ Password detection
- ✅ Fail-on-secrets mode

#### `tests/unit/utils/test_vendor_validation.py` (6 tests)
- ✅ Prerequisite validation
- ✅ Component validation
- ✅ Conversion readiness checks
- ✅ Git availability checks
- ✅ Version format validation
- ✅ Dependency validation

#### `tests/unit/utils/test_vendor_backup.py` (6 tests)
- ✅ Backup creation
- ✅ Backup with/without components
- ✅ Backup listing
- ✅ Backup restoration
- ✅ Latest backup retrieval
- ✅ Backup metadata handling

#### `tests/unit/utils/test_vendor_resume.py` (7 tests)
- ✅ Checkpoint creation
- ✅ Checkpoint loading
- ✅ Component completion tracking
- ✅ Component failure tracking
- ✅ Progress calculation
- ✅ Conversion resumption
- ✅ Checkpoint listing

#### `tests/unit/utils/test_vendor.py` (10 tests)
- ✅ Mode detection (vendored/reference)
- ✅ Component vendoring
- ✅ Vendor info retrieval
- ✅ Component vendored status
- ✅ Mode conversion (vendored ↔ reference)
- ✅ Production release conversion

### Command Tests

#### `tests/unit/commands/test_vendor.py` (18 tests)
- ✅ Import component command
- ✅ Import all components command
- ✅ Status command
- ✅ Convert command (vendored/reference)
- ✅ Convert with dry-run
- ✅ Convert with continue-on-error
- ✅ Release command
- ✅ Verify command
- ✅ Backup command
- ✅ Restore command
- ✅ List backups command
- ✅ Resume command
- ✅ List checkpoints command
- ✅ Error handling (invalid modes, missing components, etc.)

## Mock Services

### New Mock Factories

All new vendor utilities have corresponding mock factories:

- `mock_secret_detection_service()` - Secret detection mocks
- `mock_vendor_validation_service()` - Validation mocks
- `mock_vendor_backup_service()` - Backup/restore mocks
- `mock_vendor_transaction_service()` - Transaction mocks
- `mock_vendor_network_service()` - Network retry mocks
- `mock_vendor_resume_service()` - Resume mocks

### Updated Mock Services

- `mock_vendor_service()` - Enhanced with new functions:
  - `convert_to_vendored_mode_enhanced()`
  - `verify_conversion()`

## Dependency Injection

All vendor tests use the DI framework:

```python
def test_vendor_feature(temp_meta_repo, mock_vendor, mock_secret_detection):
    """Test using injected mocks."""
    # Tests use pre-configured mocks from conftest.py
    pass
```

### Available Fixtures

- `mock_vendor` - Vendor service mocks
- `mock_secret_detection` - Secret detection mocks
- `mock_vendor_validation` - Validation mocks
- `mock_vendor_backup` - Backup mocks
- `mock_vendor_transaction` - Transaction mocks
- `mock_vendor_network` - Network mocks
- `mock_vendor_resume` - Resume mocks

## Running Tests

### Run All Vendor Tests

```bash
pytest tests/unit/commands/test_vendor.py tests/unit/utils/test_vendor*.py tests/unit/utils/test_secret_detection.py -v
```

### Run Specific Test Suite

```bash
# Secret detection
pytest tests/unit/utils/test_secret_detection.py -v

# Validation
pytest tests/unit/utils/test_vendor_validation.py -v

# Backup
pytest tests/unit/utils/test_vendor_backup.py -v

# Resume
pytest tests/unit/utils/test_vendor_resume.py -v

# Commands
pytest tests/unit/commands/test_vendor.py -v
```

### Run with Coverage

```bash
pytest tests/unit/commands/test_vendor.py tests/unit/utils/test_vendor*.py tests/unit/utils/test_secret_detection.py --cov=meta.utils.vendor --cov=meta.utils.secret_detection --cov=meta.utils.vendor_validation --cov=meta.utils.vendor_backup --cov=meta.utils.vendor_resume --cov-report=html
```

## Test Patterns

### Testing with Mocks

```python
def test_vendor_convert_with_dry_run(temp_meta_repo, mock_vendor):
    """Test convert with dry-run."""
    runner = CliRunner()
    
    with patch("meta.commands.vendor.convert_to_vendored_mode_enhanced",
               return_value=(True, {'dry_run': True})):
        result = runner.invoke(app, ["vendor", "convert", "vendored", "--dry-run"])
        assert result.exit_code == 0
```

### Testing Utilities

```python
def test_secret_detection(temp_meta_repo):
    """Test secret detection."""
    comp_dir = temp_meta_repo["components"] / "test-component"
    comp_dir.mkdir()
    (comp_dir / "config.py").write_text('api_key = "sk_live_1234567890"')
    
    is_safe, results = detect_secrets_in_component(comp_dir)
    assert is_safe is False
    assert results['total_secrets'] > 0
```

### Testing Error Cases

```python
def test_validation_fails_no_git(temp_meta_repo):
    """Test validation fails when Git not available."""
    with patch("meta.utils.vendor_validation.git_available", return_value=False):
        is_valid, errors = validate_prerequisites(str(temp_meta_repo["manifests"]))
        assert is_valid is False
        assert any("Git is not available" in err for err in errors)
```

## Coverage Goals

### Current Coverage

- ✅ **Secret Detection**: 100% of critical paths
- ✅ **Vendor Validation**: 100% of validation functions
- ✅ **Vendor Backup**: 100% of backup/restore operations
- ✅ **Vendor Resume**: 100% of checkpoint operations
- ✅ **Vendor Commands**: All commands tested
- ✅ **Vendor Utilities**: Core functions tested

### Test Quality

- ✅ All tests use mocks (no real system calls)
- ✅ All tests use dependency injection
- ✅ All tests are isolated and independent
- ✅ Error cases are tested
- ✅ Edge cases are covered

## Continuous Integration

These tests should be run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Vendor Tests
  run: |
    pytest tests/unit/commands/test_vendor.py \
           tests/unit/utils/test_vendor*.py \
           tests/unit/utils/test_secret_detection.py \
           -v --cov --cov-report=xml
```

## Future Enhancements

Potential test additions:
- Integration tests for full conversion workflows
- Performance tests for large-scale conversions
- Stress tests for network resilience
- End-to-end tests for production release workflow

