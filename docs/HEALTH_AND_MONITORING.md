# Health and Monitoring

## Overview

The meta-repo CLI provides health checks and monitoring capabilities to quickly validate that components are working correctly before deployment or after incidents.

## Health Checks

### Purpose

Quick validation that components are working correctly before deployment or after incidents.

### Commands

#### Check Single Component

```bash
meta health --component scraper-capabilities
meta health --component scraper-capabilities --env prod
meta health --component scraper-capabilities --build --tests
```

#### Check All Components

```bash
meta health --all
meta health --all --env staging
meta health --all --build --tests
```

### What It Checks

- **Exists** - Component directory exists
- **Version** - Component version matches manifest/lock file
- **Dependencies** - All dependencies are available
- **Lock File Sync** - Component matches lock file (if using locked mode)
- **Builds** - Component builds successfully (optional, `--build`)
- **Tests** - Component tests pass (optional, `--tests`)

### Health Check Output

```
Component: scraper-capabilities
  Status: ✓ Healthy
  Version: v3.0.1 (matches manifest)
  Dependencies: ✓ All available
  Lock File: ✓ In sync
  Build: ✓ Successful
  Tests: ✓ Passing
```

### Benefits

- **Quick Validation** - Verify system health in seconds
- **Pre-Deployment** - Catch issues before deploying
- **Post-Incident** - Verify recovery after incidents
- **CI/CD Integration** - Use in pipelines to verify deployments

## CI/CD Integration

### Use in Pipelines

```yaml
# GitHub Actions example
- run: meta health --all --env staging --build --tests
```

### Exit Codes

- `0` - All components healthy
- `1` - One or more components unhealthy

This allows health checks to fail CI/CD pipelines when issues are detected.

## Integration with Other Systems

### Rollback

Use health checks to verify rollback success:

```bash
# Rollback component
meta rollback component my-component --to-version v1.0.0

# Verify rollback
meta health --component my-component --env prod
```

### Apply Command

Health checks can be run after apply:

```bash
# Apply components
meta apply --all --env prod

# Verify health
meta health --all --env prod
```

### Lock Files

Health checks verify lock file sync:

```bash
# Generate lock file
meta lock --env prod

# Apply with lock file
meta apply --locked --env prod

# Verify lock file sync
meta health --all --env prod
```

## Best Practices

1. **Pre-Deployment** - Always run health checks before deployment
2. **Post-Deployment** - Verify health after deployment
3. **Post-Incident** - Verify recovery after incidents
4. **CI/CD Integration** - Include health checks in pipelines
5. **Build and Test** - Use `--build` and `--tests` flags for comprehensive checks

## Implementation Details

### Files

- `meta/utils/health.py` - Health check utilities
- `meta/commands/health.py` - Health check commands

### Health Check Process

1. Check component exists
2. Verify version matches manifest/lock file
3. Check dependencies are available
4. Verify lock file sync (if using locked mode)
5. Optionally build component (`--build`)
6. Optionally run tests (`--tests`)
7. Report health status

## Benefits

1. **Production Ready** - Health checks catch issues early
2. **Quick Validation** - Verify system health in seconds
3. **CI/CD Integration** - Use in pipelines to verify deployments
4. **Recovery Verification** - Verify recovery after incidents
5. **Comprehensive** - Check existence, version, dependencies, builds, and tests

