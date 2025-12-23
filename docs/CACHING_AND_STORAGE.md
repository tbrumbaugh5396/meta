# Caching and Storage

## Overview

The meta-repo CLI provides advanced caching and content-addressed storage to speed up builds, enable build artifact sharing, and provide maximum reproducibility.

## Advanced Caching

### Purpose

Cache build artifacts to speed up subsequent builds by reusing unchanged artifacts.

### Commands

#### Build and Cache

```bash
meta cache build scraper-capabilities --source bazel-bin/scraper_capabilities
```

Builds and caches an artifact with automatic cache key computation.

#### Retrieve from Cache

```bash
meta cache get scraper-capabilities --target bazel-bin/scraper_capabilities
```

Retrieves cached artifact if available.

#### Invalidate Cache

```bash
meta cache invalidate --component scraper-capabilities
meta cache invalidate --all
```

Removes cache entries.

#### List Cache Entries

```bash
meta cache list
```

Shows all cached artifacts.

#### Cache Statistics

```bash
meta cache stats
```

Shows cache size and usage statistics.

### Cache Key Computation

Cache keys are computed from:
- Component version
- Build target
- Dependency versions
- Source file hashes

Same inputs = same cache key = cache hit!

### Benefits

- **Speed** - Faster builds by reusing artifacts
- **Efficiency** - Reduce redundant work
- **Cost** - Lower compute costs
- **Reliability** - Deterministic cache keys

## Remote Cache Support

### Purpose

Share build artifacts across machines and teams using S3 or Google Cloud Storage.

### S3 Support

```bash
# Cache with S3
meta cache build component --source path/ --remote s3://my-bucket/cache
meta cache get component --target path/ --remote s3://my-bucket/cache
```

### GCS Support

```bash
# Cache with GCS
meta cache build component --source path/ --remote gs://my-bucket/cache
meta cache get component --target path/ --remote gs://my-bucket/cache
```

### Automatic Fallback

If remote cache is unavailable, the system automatically falls back to local cache.

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

## Content-Addressed Storage (Nix-like)

### Purpose

Content-addressed store for deterministic builds, deduplication, and instant rollback.

### Commands

#### Add to Store

```bash
meta store add scraper-capabilities --source bazel-bin/scraper_capabilities
```

Adds artifact to content-addressed store. Hash computed from all inputs.

#### Query Store

```bash
meta store query abc123def456...
```

Queries store for artifact by content hash.

#### Retrieve from Store

```bash
meta store get abc123def456... --target output/
```

Retrieves artifact from store by content hash.

#### List Store Entries

```bash
meta store list
```

Lists all entries in the store.

#### Store Statistics

```bash
meta store stats
```

Shows store size and usage.

### Remote Store Support

```bash
# Store with S3
meta store add component --source path/ --remote s3://my-bucket/store
meta store get hash --target path/ --remote s3://my-bucket/store

# Store with GCS
meta store add component --source path/ --remote gs://my-bucket/store
meta store get hash --target path/ --remote gs://my-bucket/store
```

### Store Structure

```
.meta-store/
├── ab/
│   ├── abc123def456.../
│   │   └── [artifact files]
│   └── abc123def456....metadata.json
└── cd/
    └── cdef789012.../
```

### Benefits

- **Reproducibility** - Same inputs = same hash = same output
- **Deduplication** - Store only unique artifacts
- **Rollback** - Instant state switching
- **Sharing** - Share builds across machines

## Garbage Collection

### Purpose

Clean up unused cache and store entries to save disk space.

### Commands

```bash
meta gc store  # Remove unreferenced store entries
meta gc cache  # Remove old cache entries
meta gc all    # Clean both store and cache
```

### Benefits

- **Disk Space** - Free up space from unused artifacts
- **Performance** - Faster lookups with smaller stores
- **Maintenance** - Automated cleanup

## Integration

Caching and storage work together with other systems:

```bash
# 1. Apply with caching
meta apply --locked --env prod  # Uses cache if available

# 2. Cache to remote S3
meta cache build component --source build/ --remote s3://bucket/cache

# 3. Add to store for sharing
meta store add component-name --source build-output/

# 4. Garbage collection
meta gc all
```

## Implementation Details

### Files

- `meta/utils/cache.py` - Cache management
- `meta/utils/cache_keys.py` - Cache key computation
- `meta/utils/remote_cache.py` - S3/GCS backend support
- `meta/utils/content_hash.py` - Content hashing
- `meta/utils/store.py` - Content-addressed store
- `meta/utils/gc.py` - Garbage collection
- `meta/commands/cache.py` - Cache management commands
- `meta/commands/store.py` - Store management commands
- `meta/commands/gc.py` - Garbage collection commands

### Dependencies

**Optional dependencies** (only needed for remote cache/store):
- `boto3>=1.26.0` - For S3 support
- `google-cloud-storage>=2.10.0` - For GCS support

Install with:
```bash
pip install boto3  # For S3
pip install google-cloud-storage  # For GCS
```

## Benefits Summary

1. **Performance** - Faster builds through caching
2. **Reproducibility** - Content-addressed storage ensures identical builds
3. **Team Collaboration** - Share builds across team members
4. **Cost Savings** - Reduce redundant builds
5. **Flexibility** - Works with or without remote backends
6. **Efficiency** - Deduplication and garbage collection

