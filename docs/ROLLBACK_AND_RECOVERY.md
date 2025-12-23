# Rollback and Recovery

## Overview

The meta-repo CLI provides comprehensive rollback capabilities to quickly recover from issues by rolling back components to previous versions, commits, or lock file states.

## Rollback Command

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

## Rollback Workflows

### Production Incident Recovery

```bash
# 1. Identify the issue
meta health --all --env prod

# 2. List available rollback targets
meta rollback list --component problematic-component

# 3. Rollback to previous version
meta rollback component problematic-component --to-version v1.0.0

# 4. Verify recovery
meta health --all --env prod
```

### Rollback from Lock File

```bash
# 1. Identify previous working lock file
meta rollback list

# 2. Rollback entire system to previous lock file state
meta rollback lock manifests/components.lock.prod.previous.yaml

# 3. Verify all components
meta health --all --env prod
```

### Rollback from Store

```bash
# 1. Find store entry for previous working state
meta store list

# 2. Rollback component from store
meta rollback store component-name abc123def456...

# 3. Verify component
meta health --component component-name
```

## Integration with Other Systems

### Changesets

Rollback can be integrated with changesets for atomic rollback:

```bash
# Rollback a changeset
meta changeset rollback abc12345
```

This rolls back all commits associated with the changeset across all repositories.

### Lock Files

Rollback can use lock files to restore exact previous states:

```bash
# Rollback to previous lock file
meta rollback lock manifests/components.lock.prod.previous.yaml
```

### Health Checks

Use health checks to verify rollback success:

```bash
# Rollback component
meta rollback component my-component --to-version v1.0.0

# Verify rollback
meta health --component my-component --env prod
```

## Snapshot Management

### Create Snapshots

Create snapshots before major changes:

```bash
# Create snapshot before deployment
meta rollback snapshot --output pre-deployment-snapshot.yaml

# Create snapshot for specific components
meta rollback snapshot --components "comp1,comp2" --output snapshot.yaml
```

### Restore from Snapshots

```bash
# Restore from snapshot
meta rollback snapshot --restore pre-deployment-snapshot.yaml
```

## Best Practices

1. **Create Snapshots** - Create snapshots before major deployments
2. **Test Rollback** - Test rollback procedures in staging
3. **Document Targets** - Keep track of known-good versions
4. **Verify After Rollback** - Always verify system health after rollback
5. **Use Lock Files** - Use lock files for reproducible rollbacks

## Implementation Details

### Files

- `meta/utils/rollback.py` - Rollback utilities
- `meta/commands/rollback.py` - Rollback commands

### Rollback Process

1. Identify rollback target (version, commit, lock file, or store entry)
2. Validate target exists and is accessible
3. Checkout component to target state
4. Update manifest/lock file if needed
5. Verify rollback success

## Benefits

1. **Production Ready** - Rollback is critical for production
2. **Fast Recovery** - Rollback in seconds, not minutes
3. **Multiple Options** - Rollback to version, commit, lock file, or store
4. **Safety** - Lists available targets before rolling back
5. **Integration** - Works with changesets, lock files, and health checks

