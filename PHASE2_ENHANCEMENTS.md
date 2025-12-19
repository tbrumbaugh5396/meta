# Phase 2 Enhancements: Complete Guide

## Overview

Phase 2 adds five major enhancements to the meta-repo CLI:

1. **Multi-Environment Lock Files** - Environment-specific lock files for different deployment stages
2. **Enhanced Package Management** - Package lock files, security scanning, license checking, dependency graphs
3. **Dependency Conflict Resolution** - Automatic detection and resolution of dependency conflicts
4. **Advanced Caching** - Build artifact caching for faster builds
5. **Content-Addressed Storage** - Nix-like content-addressed store for deterministic builds

## 1. Multi-Environment Lock Files

### Purpose

Generate and manage separate lock files for different environments (dev, staging, prod), allowing different component versions per environment while maintaining reproducibility.

### Usage

#### Generate Environment-Specific Lock File

```bash
meta lock --env dev
meta lock --env staging
meta lock --env prod
```

This generates `manifests/components.lock.{env}.yaml` for each environment.

#### Promote Lock Files

```bash
meta lock promote dev staging  # Promote dev lock to staging
meta lock promote staging prod  # Promote staging lock to prod
```

#### Compare Lock Files

```bash
meta lock compare dev prod  # Compare dev and prod lock files
```

#### Use Environment Lock Files

```bash
meta apply --locked --env prod  # Uses components.lock.prod.yaml
```

### Benefits

- **Environment Isolation** - Different versions per environment
- **Safe Promotion** - Promote tested configurations
- **Easy Comparison** - See differences between environments
- **Reproducibility** - Each environment has exact commit SHAs

## 2. Enhanced Package Management

### Purpose

Manage package manager dependencies (npm, pip, cargo, go) with lock files, security scanning, license checking, and dependency visualization.

### Commands

#### Generate Package Lock Files

```bash
meta deps lock --component scraper-capabilities
meta deps lock --all  # Generate locks for all components
```

Generates:
- `package-lock.json` for npm
- `requirements.lock` for pip
- `Cargo.lock` for cargo
- `go.sum` for go

#### Security Vulnerability Scanning

```bash
meta deps audit --component scraper-capabilities
meta deps audit --all
```

Scans dependencies for known vulnerabilities using:
- `npm audit` for npm
- `pip-audit` or `safety` for pip

#### License Compliance Checking

```bash
meta deps licenses --component scraper-capabilities
meta deps licenses --all
meta deps licenses --allowed "MIT,Apache-2.0,BSD-3-Clause"
```

Checks dependency licenses for compliance using:
- `license-checker` for npm
- `pip-licenses` for pip

#### Dependency Graph Visualization

```bash
meta deps graph --component scraper-capabilities --format dot --output graph.dot
meta deps graph --format json  # Component dependency graph
```

Generates dependency graphs in DOT or JSON format.

### Benefits

- **Security** - Catch vulnerabilities early
- **Compliance** - Ensure license compatibility
- **Visibility** - Understand dependency relationships
- **Reproducibility** - Lock files ensure consistent installs

## 3. Dependency Conflict Resolution

### Purpose

Detect and resolve dependency conflicts automatically using semantic versioning.

### Commands

#### Check for Conflicts

```bash
meta conflicts check
```

Detects:
- Version conflicts between components
- Incompatible dependency ranges
- Circular dependencies

#### Resolve Conflicts

```bash
meta conflicts resolve --strategy latest
meta conflicts resolve --strategy conservative
meta conflicts resolve --strategy first
meta conflicts resolve --strategy highest
```

Strategies:
- **latest** - Use latest compatible version
- **conservative** - Use lowest compatible version
- **first** - Use first requirement's version
- **highest** - Use highest version

#### Get Recommendations

```bash
meta conflicts recommend
```

Suggests dependency updates based on available versions.

### Semantic Version Support

Components can now use version ranges in `depends_on`:

```yaml
components:
  my-component:
    depends_on:
      - "dependency-component:^1.0.0"  # Caret range
      - "other-component:~2.1.0"       # Tilde range
      - "another-component:>=3.0.0"   # Greater than or equal
```

### Benefits

- **Early Detection** - Catch conflicts before deployment
- **Automatic Resolution** - Resolve conflicts automatically
- **Flexibility** - Support version ranges
- **Recommendations** - Get update suggestions

## 4. Advanced Caching

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

## 5. Content-Addressed Storage (Nix-like)

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

### Garbage Collection

```bash
meta gc store  # Remove unreferenced store entries
meta gc cache  # Remove old cache entries
meta gc all    # Clean both store and cache
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

## Integration

All Phase 2 features work together:

1. **Multi-Environment Lock Files** ensure reproducibility per environment
2. **Enhanced Package Management** ensures dependency security and compliance
3. **Dependency Conflict Resolution** prevents deployment issues
4. **Advanced Caching** speeds up builds
5. **Content-Addressed Storage** provides maximum reproducibility

### Complete Workflow

```bash
# 1. Generate environment lock files
meta lock --env dev
meta lock --env prod

# 2. Check for conflicts
meta conflicts check

# 3. Audit dependencies
meta deps audit --all

# 4. Check licenses
meta deps licenses --all

# 5. Generate package locks
meta deps lock --all

# 6. Apply with caching
meta apply --locked --env prod  # Uses cache if available

# 7. Add to store for sharing
meta store add component-name --source build-output/

# 8. Garbage collection
meta gc all
```

## Files Added

### Utilities
- `meta/utils/environment_locks.py` - Environment lock file management
- `meta/utils/package_locks.py` - Package lock file generation
- `meta/utils/security.py` - Vulnerability scanning
- `meta/utils/licenses.py` - License compliance checking
- `meta/utils/dependency_graph.py` - Dependency graph visualization
- `meta/utils/semver.py` - Semantic version parsing
- `meta/utils/conflicts.py` - Conflict detection and resolution
- `meta/utils/cache_keys.py` - Cache key computation
- `meta/utils/cache.py` - Cache management
- `meta/utils/content_hash.py` - Content hashing
- `meta/utils/store.py` - Content-addressed store
- `meta/utils/gc.py` - Garbage collection

### Commands
- `meta/commands/deps.py` - Dependency management
- `meta/commands/conflicts.py` - Conflict resolution
- `meta/commands/cache.py` - Cache management
- `meta/commands/store.py` - Store management
- `meta/commands/gc.py` - Garbage collection

### Tests
- `tests/unit/test_environment_locks.py`
- `tests/unit/test_semver.py`
- `tests/unit/test_cache.py`
- `tests/unit/test_store.py`

## Benefits Summary

1. **Reproducibility** - Lock files + content-addressed storage
2. **Security** - Vulnerability scanning
3. **Compliance** - License checking
4. **Performance** - Caching
5. **Reliability** - Conflict detection
6. **Flexibility** - Multi-environment support
7. **Efficiency** - Deduplication and garbage collection

## Next Steps

Phase 2 is complete! The meta-repo CLI now has enterprise-grade features for:
- Multi-environment deployments
- Security and compliance
- Performance optimization
- Maximum reproducibility

Consider:
- Remote cache support (S3, GCS)
- Store sharing across machines
- Advanced conflict resolution strategies
- Performance monitoring and metrics


