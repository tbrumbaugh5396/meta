# Phase 3 Enhancements: Rollback, Remote Cache, and Progress

## Overview

Phase 3 adds three critical production-ready features:

1. **Rollback Command** - Quick rollback to previous states
2. **Remote Cache/Store** - S3 and GCS support for sharing builds
3. **Progress Indicators & Parallel Execution** - Better UX and performance

## 1. Rollback Command

### Purpose

Quickly rollback components to previous versions, commits, or lock file states. Critical for production incidents.

### Commands

#### Rollback Component to Version/Commit

```bash
meta rollback component scraper-capabilities --to-version v2.0.0
meta rollback component scraper-capabilities --to-commit abc123def456
```

#### Rollback from Lock File

```bash
meta rollback lock manifests/components.lock.prod.yaml
meta rollback lock manifests/components.lock.dev.yaml --component scraper-capabilities
```

#### Rollback from Store

```bash
meta rollback store scraper-capabilities abc123def456...
```

#### List Available Rollback Targets

```bash
meta rollback list
meta rollback list --component scraper-capabilities
```

#### Create Rollback Snapshot

```bash
meta rollback snapshot --output backup-snapshot.yaml
meta rollback snapshot --components "comp1,comp2" --output snapshot.yaml
```

### Benefits

- **Fast Recovery** - Rollback in seconds, not minutes
- **Multiple Options** - Rollback to version, commit, lock file, or store entry
- **Safe** - Lists available targets before rolling back
- **Snapshots** - Create checkpoints for easy rollback

## 2. Remote Cache/Store Support

### Purpose

Share build artifacts across machines and teams using S3 or Google Cloud Storage.

### S3 Support

```bash
# Cache with S3
meta cache build component --source path/ --remote s3://my-bucket/cache
meta cache get component --target path/ --remote s3://my-bucket/cache

# Store with S3
meta store add component --source path/ --remote s3://my-bucket/store
meta store get hash --target path/ --remote s3://my-bucket/store
```

### GCS Support

```bash
# Cache with GCS
meta cache build component --source path/ --remote gs://my-bucket/cache
meta cache get component --target path/ --remote gs://my-bucket/cache

# Store with GCS
meta store add component --source path/ --remote gs://my-bucket/store
meta store get hash --target path/ --remote gs://my-bucket/store
```

### Automatic Fallback

If remote cache/store is unavailable, the system automatically falls back to local cache/store.

### Configuration

Set environment variables for authentication:

**S3:**
```bash
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_DEFAULT_REGION=us-east-1
```

**GCS:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

### Benefits

- **Team Sharing** - Share builds across team members
- **CI/CD Speed** - Faster CI builds by reusing artifacts
- **Cost Savings** - Reduce redundant builds
- **Reliability** - Automatic fallback to local

## 3. Progress Indicators & Parallel Execution

### Purpose

Better user experience with progress bars and faster execution with parallel processing.

### Progress Indicators

Progress bars automatically appear for operations on multiple components:

```bash
meta apply --all
# Shows: Applying components: [████████████░░░░░░░░] 60% (3/5)
```

Disable progress bars:
```bash
meta apply --all --no-progress
```

### Parallel Execution

Apply multiple components in parallel:

```bash
meta apply --all --parallel --jobs 4
```

This:
- Respects dependency order (independent components run in parallel)
- Uses ThreadPoolExecutor for concurrent execution
- Shows progress for parallel operations
- Defaults to 4 parallel jobs (configurable with `--jobs`)

### Benefits

- **Better UX** - See progress for long operations
- **Faster** - Parallel execution speeds up large deployments
- **Configurable** - Control number of parallel jobs
- **Safe** - Still respects dependency order

## Integration

All three features work together:

```bash
# 1. Apply with progress and parallel execution
meta apply --all --parallel --jobs 4 --progress

# 2. Cache to remote S3
meta cache build component --source build/ --remote s3://bucket/cache

# 3. If something goes wrong, rollback quickly
meta rollback component component-name --to-version v1.0.0
```

## Files Added

### Utilities
- `meta/utils/rollback.py` - Rollback utilities
- `meta/utils/remote_cache.py` - S3/GCS backend support
- `meta/utils/progress.py` - Progress indicators

### Commands
- `meta/commands/rollback.py` - Rollback commands

### Tests
- `tests/unit/test_rollback.py`
- `tests/unit/test_remote_cache.py`
- `tests/unit/test_progress.py`

## Files Modified

- `meta/utils/cache.py` - Added remote backend support
- `meta/utils/store.py` - Added remote backend support
- `meta/commands/cache.py` - Added `--remote` flag
- `meta/commands/store.py` - Added `--remote` flag
- `meta/commands/apply.py` - Added `--parallel`, `--jobs`, `--progress` flags
- `meta/cli.py` - Added rollback command
- `requirements.txt` - Added boto3 and google-cloud-storage (optional)

## Dependencies

**Optional dependencies** (only needed for remote cache/store):
- `boto3>=1.26.0` - For S3 support
- `google-cloud-storage>=2.10.0` - For GCS support

Install with:
```bash
pip install boto3  # For S3
pip install google-cloud-storage  # For GCS
```

## Benefits Summary

1. **Production Ready** - Rollback is critical for production
2. **Performance** - Remote cache speeds up CI/CD significantly
3. **Team Collaboration** - Share builds across team
4. **Better UX** - Progress bars and parallel execution
5. **Flexibility** - Works with or without remote backends

## Next Steps

Optional enhancements:
- Rollback history tracking
- Remote cache statistics
- Cache warming strategies
- More cloud providers (Azure Blob Storage, etc.)


