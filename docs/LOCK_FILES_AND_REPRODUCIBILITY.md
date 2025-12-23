# Lock Files and Reproducibility

## Overview

Lock files ensure reproducible builds by pinning exact commit SHAs (in reference mode) or semantic versions (in vendored mode) instead of just version tags. This prevents "works on my machine" issues and ensures all environments use identical code.

## Basic Lock Files

### Purpose

Lock files pin exact component versions to ensure reproducible builds across all environments and team members.

### Usage

#### Generate Lock File

```bash
meta lock
```

This generates `manifests/components.lock.yaml` with exact commit SHAs (reference mode) or semantic versions (vendored mode) for all components.

#### Validate Lock File

```bash
meta lock validate
```

Validates that the lock file matches the current `components.yaml` manifest.

#### Use Lock File for Apply

```bash
meta apply --locked
```

Applies components using exact versions from the lock file instead of version tags.

### Lock File Format

**Reference Mode:**
```yaml
generated_at: "2024-01-15T10:30:00Z"
components:
  scraper-capabilities:
    version: "v3.0.1"
    commit: "abc123def456789..."
    repo: "git@github.com:yourorg/scraper-capabilities.git"
    type: "bazel"
    build_target: "//scraper_capabilities:all"
    depends_on:
      - infrastructure-primitives
      - agent-core
```

**Vendored Mode:**
```yaml
generated_at: "2024-01-15T10:30:00Z"
components:
  scraper-capabilities:
    version: "v3.0.1"
    vendored_at: "2024-01-15T10:30:00Z"
    repo: "git@github.com:yourorg/scraper-capabilities.git"
    type: "bazel"
    build_target: "//scraper_capabilities:all"
```

### Best Practices

- **Commit lock files to Git** - Ensures team uses same versions
- **Regenerate after version updates** - Run `meta lock` after changing component versions
- **Use in CI/CD** - Always use `--locked` flag in production deployments
- **Validate in CI** - Add `meta lock validate` to your CI pipeline

## Multi-Environment Lock Files

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
- **Reproducibility** - Each environment has exact versions

## Changeset Integration

Lock file updates can be associated with changesets for atomic cross-repo operations:

```bash
meta lock --changeset abc12345
```

This records the lock file update in the changeset, allowing you to track which lock file changes belong to which logical change.

## Complete Workflow

```bash
# 1. Validate system
meta validate

# 2. Generate lock file for reproducibility
meta lock

# 3. Generate environment-specific lock files
meta lock --env dev
meta lock --env staging
meta lock --env prod

# 4. Apply components using lock file
meta apply --locked --env prod

# 5. In CI/CD, always use locked mode
meta apply --locked --skip-packages  # Skip packages if pre-installed
```

## Implementation Details

### Files

- `meta/utils/lock.py` - Lock file generation and validation
- `meta/utils/environment_locks.py` - Environment lock file management
- `meta/commands/lock.py` - Lock file CLI command

### Lock File Generation

The lock file generation process:

1. Reads `components.yaml` manifest
2. For each component:
   - In **reference mode**: Resolves version tag to exact commit SHA
   - In **vendored mode**: Uses semantic version from manifest
3. Records all component metadata
4. Writes lock file to disk

### Validation

Lock file validation checks:

1. All components in manifest exist in lock file
2. All components in lock file exist in manifest
3. Version/commit information matches
4. Dependencies are consistent

## Benefits

1. **Reproducibility** - Lock files ensure identical builds across environments
2. **Team Consistency** - All team members use same versions
3. **CI/CD Reliability** - Production deployments use exact versions
4. **Environment Safety** - Different versions per environment with promotion workflow

