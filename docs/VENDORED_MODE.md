# Vendored Mode: Linus-Safe Materialization

## Overview

Vendored mode provides a "Linus-safe" alternative to reference-based meta-repos by copying component source code directly into the meta-repo, making it self-contained and authoritative.

## Key Differences

| Aspect | Reference Mode | Vendored Mode |
|--------|---------------|---------------|
| Component storage | Git repos in `components/` | Source code in `components/` |
| Lock files | Commit SHAs | Semantic versions |
| Authority | Child repos | Meta-repo |
| Self-contained | No | Yes |
| Atomicity | Simulated (changesets) | True (single commit) |
| Linus-safe | No | Yes |

## Why Vendored Mode?

### The Problem with Reference Mode

Reference mode (the default) stores components as git repositories, which means:

- Meta-repo commits contain pointers, not actual code
- System state requires external repositories
- History is fragmented across repos
- Not self-contained

### The Solution: Vendored Mode

Vendored mode solves this by:

- **Materializing state**: Component source is copied into meta-repo
- **Self-contained commits**: Each meta-repo commit contains complete system state
- **True atomicity**: System changes are single commits
- **Bisectable**: Can bisect using meta-repo alone
- **Linus-safe**: Meets Linus Torvalds' standards for repository design

## Usage

### Enable Vendored Mode

Add `meta.mode: "vendored"` to your `components.yaml`:

```yaml
# manifests/components.yaml
meta:
  mode: "vendored"  # Enable vendored mode

components:
  agent-core:
    repo: "git@github.com:org/agent-core.git"
    version: "v1.2.3"  # Semantic version only
    type: "bazel"
    build_target: "//agent_core:all"
```

### Import Components

```bash
# Import single component
meta vendor import agent-core

# Import all components
meta vendor import-all

# Force re-import (updates to new version)
meta vendor import-all --force

# Check status
meta vendor status
```

### Workflow

1. **Configure**: Set `meta.mode: "vendored"` in `components.yaml`
2. **Import**: `meta vendor import-all` copies source into meta-repo
3. **Review**: Check the vendored code in `components/`
4. **Commit**: `git add components/ && git commit -m "Vendor components"`
5. **Build**: `meta apply` works with vendored source
6. **Update**: When upstream releases new version, re-import and commit

### Example Workflow

```bash
# 1. Enable vendored mode
# Edit manifests/components.yaml to add meta.mode: "vendored"

# 2. Import components
meta vendor import-all

# 3. Review and commit
git add components/
git commit -m "Vendor all components"

# 4. Build and test
meta apply --all

# 5. When upstream updates, re-import
# Update version in components.yaml, then:
meta vendor import-all --force
git add components/
git commit -m "Update vendored components to v1.3.0"
```

## Lock Files in Vendored Mode

Lock files in vendored mode store semantic versions only (no commit SHAs):

```yaml
# manifests/components.lock.yaml
generated_at: "2024-01-15T10:30:00Z"
mode: "vendored"
components:
  agent-core:
    version: "v1.2.3"  # Semantic version only
    repo: "git@github.com:org/agent-core.git"
    type: "bazel"
    vendored_at: "2024-01-15T10:30:00Z"
```

## Benefits

- ✅ **Meta-repo commits are self-contained**: No external dependencies
- ✅ **True atomic commits**: System changes are single commits
- ✅ **Bisectable**: Can bisect using meta-repo alone
- ✅ **Linus-safe**: Meets Linus Torvalds' repository design standards
- ✅ **Reproducible**: Each commit represents a complete, buildable system
- ✅ **No external dependencies**: Works even if upstream repos disappear

## Trade-offs

- ❌ **Larger repo size**: Source code is duplicated in meta-repo
- ❌ **Manual import process**: Must explicitly import when upstream updates
- ❌ **One-way flow**: Changes flow upstream → meta-repo only (no auto-sync)
- ❌ **No live updates**: Must re-import to get upstream changes

## When to Use Vendored Mode

Use vendored mode when:

- You need Linus-safe repository design
- You want true atomic commits
- You need self-contained system state
- You prioritize reproducibility over convenience
- You can accept larger repository size

Use reference mode when:

- You need live updates from upstream
- Repository size is a concern
- You want automatic synchronization
- You're comfortable with external dependencies

## Comparison with Reference Mode

### Reference Mode Example

```bash
# components.yaml
components:
  agent-core:
    repo: "git@github.com:org/agent-core.git"
    version: "v1.2.3"

# Lock file contains:
commit: "abc123def456..."  # ← Pointer to external repo

# To get system state:
git checkout meta-repo-commit
git clone upstream-repo  # ← External dependency
```

### Vendored Mode Example

```bash
# components.yaml
meta:
  mode: "vendored"
components:
  agent-core:
    repo: "git@github.com:org/agent-core.git"
    version: "v1.2.3"

# Lock file contains:
version: "v1.2.3"  # ← Semantic version only

# To get system state:
git checkout meta-repo-commit
# ← Complete system state, no external dependencies
```

## Technical Details

### Vendor Info File

Each vendored component includes a `.vendor-info.yaml` file:

```yaml
component: agent-core
repo: git@github.com:org/agent-core.git
version: v1.2.3
vendored_at: "2024-01-15T10:30:00Z"
```

This provides provenance information while keeping the meta-repo authoritative.

### Import Process

1. Clone upstream repository to temporary directory
2. Checkout specified version/tag
3. Remove `.git` directory (no git history)
4. Copy source to `components/{name}/`
5. Create `.vendor-info.yaml` for provenance

### Apply Process

In vendored mode, `meta apply`:

1. Checks that component is vendored
2. Uses vendored source directly (no git operations)
3. Installs dependencies
4. Builds and tests

## Conversion Between Modes

### Convert to Vendored Mode

```bash
# Convert all components from reference to vendored mode
meta vendor convert vendored

# Force re-conversion
meta vendor convert vendored --force
```

This will:
1. Update `components.yaml` to set `meta.mode: "vendored"`
2. Remove git repos from `components/`
3. Vendor all components (copy source code)
4. Create `.vendor-info.yaml` files for provenance

### Convert to Reference Mode

```bash
# Convert all components from vendored to reference mode
meta vendor convert reference

# Force re-conversion
meta vendor convert reference --force
```

This will:
1. Update `components.yaml` to remove vendored mode
2. Read `.vendor-info.yaml` to get repo URLs and versions
3. Remove vendored source code
4. Clone components as git repos
5. Checkout specified versions

### Production Release Workflow

The recommended workflow is to use **reference mode for development** and **vendored mode for production**:

```bash
# ============================================
# DEVELOPMENT (Reference Mode)
# ============================================

# 1. Develop in reference mode (flexible, easy updates)
meta apply --env dev
# Components are git repos, easy to update

# 2. Test in staging (still reference mode)
meta apply --env staging
meta test --env staging

# ============================================
# PRODUCTION RELEASE (Vendored Mode)
# ============================================

# 3. Create production release (converts to vendored)
meta vendor release --env prod --version v1.0.0

# This:
# - Converts all components to vendored mode
# - Uses semantic versions from environments.yaml
# - Creates self-contained production release
# - Generates components.lock.prod.yaml

# 4. Commit and tag
git add manifests/ components/
git commit -m "Production release v1.0.0"
git tag -a v1.0.0 -m "Production release v1.0.0"

# ============================================
# PRODUCTION DEPLOYMENT
# ============================================

# 5. Deploy production (self-contained, no external deps)
git checkout v1.0.0
meta apply --env prod
# All source is in meta-repo, no git clones needed
```

### Benefits of Dev → Prod Workflow

- **Development**: Reference mode for flexibility
  - Easy updates: `git pull` in component repos
  - Fast iteration: No re-vendoring needed
  - Live changes: Work with latest code

- **Production**: Vendored mode for stability
  - Self-contained: No external dependencies
  - Immutable: Semantic versions locked
  - Linus-safe: Complete system state in one commit
  - Reproducible: Lock file with exact versions

## Migration

To migrate from reference mode to vendored mode:

1. Add `meta.mode: "vendored"` to `components.yaml`
2. Run `meta vendor import-all` OR `meta vendor convert vendored`
3. Commit vendored components
4. Update CI/CD to use vendored mode
5. Remove old git repos from `components/` (optional)

## Best Practices

1. **Commit vendored code**: Always commit vendored components to git
2. **Use semantic versions**: Only reference semantic versions, not commit SHAs
3. **Review before committing**: Check vendored code before committing
4. **Regular updates**: Re-import when upstream releases new versions
5. **Document provenance**: The `.vendor-info.yaml` files provide audit trail

## Limitations

1. **No bidirectional sync**: Cannot push changes back to upstream automatically
2. **Manual updates**: Must explicitly re-import to get upstream changes
3. **Larger repository**: Source code is duplicated
4. **Import time**: Initial import can be slow for large components

## Enhanced Features

The vendor system includes comprehensive safety, reliability, and developer experience features:

### Safety Features

#### Pre-Conversion Validation
- Validates prerequisites (Git, manifests, structure)
- Checks component configurations
- Validates dependencies
- Detects circular dependencies
- Checks for secrets (optional)

**Usage:**
```bash
# Automatic validation before conversion
meta vendor convert vendored
```

#### Secret Detection
- Scans for API keys, passwords, tokens
- Detects private keys
- Configurable patterns
- Respects exclusions

**Usage:**
```bash
# Check secrets (warns but continues)
meta vendor convert vendored --check-secrets

# Fail if secrets detected
meta vendor convert vendored --fail-on-secrets
```

#### Automatic Backup
- Creates backup before conversion
- Manual backup/restore commands
- Backup listing
- Component inclusion/exclusion

**Usage:**
```bash
# Automatic backup (default)
meta vendor convert vendored --backup

# Manual backup
meta vendor backup --name my-backup

# Restore from backup
meta vendor restore my-backup

# List backups
meta vendor list-backups
```

#### Atomic Transactions
- All-or-nothing conversion
- Automatic rollback on failure
- Checkpoint management
- Transaction logging

**Usage:**
```bash
# Atomic conversion (default)
meta vendor convert vendored --atomic

# Non-atomic (allows partial conversion)
meta vendor convert vendored --no-atomic
```

### Reliability Features

#### Network Resilience
- Automatic retry with exponential backoff
- Handles transient network failures
- Configurable retry limits
- Git operations with retry

**Automatic**: Enabled by default

#### Continue-on-Error Mode
- Continue converting other components if one fails
- Partial success instead of total failure
- Useful for large meta-repos

**Usage:**
```bash
meta vendor convert vendored --continue-on-error
```

#### Conversion Resume
- Resume from checkpoint after failure
- Skip already-converted components
- Retry failed components
- Progress tracking

**Usage:**
```bash
# Resume from latest checkpoint
meta vendor resume

# Resume from specific checkpoint
meta vendor resume --checkpoint checkpoint_20240115_120000

# List checkpoints
meta vendor list-checkpoints
```

#### Dependency-Aware Ordering
- Converts components in dependency order
- Uses topological sort
- Dependencies converted before dependents

**Automatic**: Enabled by default

### Developer Experience

#### Dry-Run Mode
- Preview changes without making them
- Identify potential issues
- Plan conversion order

**Usage:**
```bash
meta vendor convert vendored --dry-run
```

#### File Filtering (.gitignore Support)
- Respects `.gitignore` patterns during vendor
- Excludes build artifacts
- Reduces vendored size
- Cleaner vendored code

**Usage:**
```bash
# Respect .gitignore (default)
meta vendor convert vendored --respect-gitignore

# Include all files
meta vendor convert vendored --no-respect-gitignore
```

#### Conversion Verification
- Verifies conversion succeeded
- Checks file integrity
- Validates vendored state
- Reports component status

**Usage:**
```bash
# Automatic verification (default)
meta vendor convert vendored --verify

# Manual verification
meta vendor verify
```

#### Changeset Integration
- Tracks conversions in changesets
- Atomic authorship across repos
- Audit trail
- Links conversion to logical changes

**Usage:**
```bash
# Associate with changeset
meta vendor convert vendored --changeset abc12345
```

#### Semantic Version Validation
- Validates semantic version formats
- Ensures production-ready versions
- Rejects "latest" in production
- Validates version compatibility

**Automatic**: Enabled in validation

## Enhanced Conversion Commands

### Complete Example Workflow

```bash
# 1. Preview conversion (dry-run)
meta vendor convert vendored --dry-run

# 2. Validate everything is ready
meta vendor convert vendored --dry-run  # Includes validation

# 3. Convert with all safety features
meta vendor convert vendored \
  --backup \
  --atomic \
  --check-secrets \
  --verify \
  --changeset abc12345

# 4. If conversion fails, resume
meta vendor resume

# 5. Verify conversion
meta vendor verify

# 6. If needed, restore from backup
meta vendor restore backup_20240115_120000
```

### New Commands

#### `meta vendor verify`
Verify that a conversion was successful.

```bash
meta vendor verify
meta vendor verify --check-integrity
```

#### `meta vendor backup`
Create a manual backup.

```bash
meta vendor backup
meta vendor backup --name my-backup
meta vendor backup --no-include-components
```

#### `meta vendor restore <name>`
Restore from a backup.

```bash
meta vendor restore backup_20240115_120000
meta vendor restore my-backup --no-restore-components
```

#### `meta vendor list-backups`
List all available backups.

```bash
meta vendor list-backups
```

#### `meta vendor resume`
Resume a conversion from a checkpoint.

```bash
meta vendor resume
meta vendor resume --checkpoint checkpoint_20240115_120000
meta vendor resume --no-retry-failed
```

#### `meta vendor list-checkpoints`
List all available conversion checkpoints.

```bash
meta vendor list-checkpoints
```

## See Also

- [Lock Files and Reproducibility](./LOCK_FILES_AND_REPRODUCIBILITY.md) - Reproducible builds
- [Changeset System](./CHANGESET_SYSTEM.md) - Atomic cross-repo operations
- [Component Operations](./COMPONENT_OPERATIONS.md) - Apply and validate commands
- [README.md](../README.md) - Complete documentation

[↑ Back to Table of Contents](../README.md#table-of-contents)

