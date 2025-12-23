# Component Operations

## Overview

The meta-repo CLI provides comprehensive commands for managing components: applying changes, validating configurations, planning deployments, and checking status.

## Apply Command

### Purpose

Apply changes to components, installing dependencies, building, and deploying.

### Basic Usage

```bash
# Apply all components
meta apply --all

# Apply specific component
meta apply --component scraper-capabilities

# Apply with environment
meta apply --all --env prod
```

### Options

- `--component, -c` - Apply specific component
- `--all, -a` - Apply all components
- `--env, -e` - Environment to apply (default: "dev")
- `--locked` - Use lock file for exact versions
- `--skip-packages` - Skip package installation
- `--parallel` - Apply components in parallel
- `--jobs` - Number of parallel jobs (default: 4)
- `--progress` - Show progress bars
- `--no-progress` - Hide progress bars

### Locked Mode

Apply using exact versions from lock file:

```bash
meta apply --locked --env prod
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

### Package Installation

Package installation happens automatically during apply:

```bash
meta apply --all
# Automatically installs npm, pip, cargo, go dependencies
```

Skip package installation:

```bash
meta apply --all --skip-packages
```

### Example Output

```
Applying changes for component: scraper-capabilities
Detected package managers: npm, pip
Installing npm dependencies from package.json...
npm dependencies installed for components/scraper-capabilities
Installing pip dependencies from requirements.txt...
pip dependencies installed for components/scraper-capabilities
Building Bazel target: //scraper_capabilities:all
Successfully applied changes for scraper-capabilities
```

## Validate Command

### Purpose

Validates system correctness, including component dependencies, versions, and configurations.

### Basic Usage

```bash
# Validate entire system
meta validate

# Validate specific environment
meta validate --env staging

# Skip specific validations
meta validate --skip-bazel --skip-git
```

### Options

- `--env, -e` - Environment to validate (default: "dev")
- `--manifests, -m` - Manifests directory (default: "manifests")
- `--skip-bazel` - Skip Bazel validation
- `--skip-git` - Skip Git validation

### What It Validates

- Component versions
- Component dependencies (all `depends_on` entries exist)
- No circular dependencies
- Feature contracts
- Manifest validity
- Lock file sync (if using locked mode)

### Example Output

```
Validating system...
✓ All components have valid versions
✓ All dependencies exist
✓ No circular dependencies detected
✓ All features are valid
✓ System validation successful
```

## Plan Command

### Purpose

Shows planned changes before applying, allowing you to review what will happen.

### Basic Usage

```bash
# Plan for all components
meta plan --all

# Plan for specific component
meta plan --component scraper-capabilities

# Plan for environment
meta plan --env staging
```

### Options

- `--component, -c` - Plan for specific component
- `--all, -a` - Plan for all components
- `--env, -e` - Environment to plan for (default: "dev")
- `--manifests, -m` - Manifests directory (default: "manifests")

### Example Output

```
Planning changes for environment: staging

Components to apply:
  scraper-capabilities (v3.0.1)
    - Will clone from: git@github.com:org/scraper-capabilities.git
    - Will checkout: v3.0.1
    - Dependencies: infrastructure-primitives, agent-core
    - Package managers: npm, pip
    - Build target: //scraper_capabilities:all

Dependencies will be applied in order:
  1. infrastructure-primitives
  2. agent-core
  3. scraper-capabilities
```

## Status Command

### Purpose

Shows current status of components, including versions, dependencies, and sync state.

### Basic Usage

```bash
# Show status of all components
meta status

# Show status for environment
meta status --env prod
```

### Options

- `--env, -e` - Environment to check (default: "dev")
- `--component, -c` - Show status for specific component

### Example Output

```
Component Status:

scraper-capabilities
  Version: v3.0.1
  Status: ✓ Synced
  Dependencies: ✓ All available
  Lock File: ✓ In sync

agent-core
  Version: v2.1.0
  Status: ⚠ Out of sync
  Dependencies: ✓ All available
  Lock File: ⚠ Needs update
```

## Integration

All component operations work together:

```bash
# 1. Plan changes
meta plan --env staging

# 2. Validate system
meta validate --env staging

# 3. Apply changes
meta apply --all --env staging --locked

# 4. Check status
meta status --env staging

# 5. Verify health
meta health --all --env staging
```

## Dependency Ordering

All operations respect component dependencies:

- Components with no dependencies are processed first
- Dependencies are processed before dependents
- Transitive dependencies are resolved automatically

## Error Handling

### Continue on Error

Continue processing other components if one fails:

```bash
meta apply --all --continue-on-error
```

### Retry Failed Components

Retry failed components automatically:

```bash
meta apply --all --retry 3
```

## Progress Indicators

Progress bars automatically appear for operations on multiple components:

```bash
meta apply --all
# Shows: Applying components: [████████████░░░░░░░░] 60% (3/5)
```

Disable progress bars:

```bash
meta apply --all --no-progress
```

## Implementation Details

### Files

- `meta/commands/apply.py` - Apply command implementation
- `meta/commands/validate.py` - Validate command implementation
- `meta/commands/plan.py` - Plan command implementation
- `meta/utils/git.py` - Git operations
- `meta/utils/packages.py` - Package management
- `meta/utils/dependencies.py` - Dependency resolution

### Apply Process

1. Resolve component dependencies (topological sort)
2. For each component (in dependency order):
   - Clone/checkout component (if needed)
   - Install package dependencies
   - Build component
   - Run tests (optional)
3. Report results

## Benefits

1. **Automation** - Automated component management
2. **Dependency Awareness** - Automatic dependency ordering
3. **Reproducibility** - Lock file support ensures exact versions
4. **Parallel Execution** - Faster deployments with parallel processing
5. **Error Recovery** - Continue-on-error and retry capabilities
6. **Progress Visibility** - See what's happening with progress bars

