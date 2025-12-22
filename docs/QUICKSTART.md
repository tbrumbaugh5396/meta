# Meta-Repo CLI Quick Start

## Installation

```bash
cd meta-repo
pip install -r requirements.txt
pip install -e .
```

## Basic Usage

### 1. Check System Status

```bash
meta status --env dev
```

This shows:
- Current component versions
- Desired versions from manifests
- Sync status

### 2. Validate System

```bash
meta validate --env dev
```

This validates:
- Component version formats
- Bazel target existence
- Feature contracts
- Dependency cycles

### 3. Plan Changes

```bash
meta plan --env staging
```

Shows what changes would be made:
- Version upgrades
- Version downgrades
- New components

### 4. Apply Changes

```bash
meta apply --env staging
```

This will:
- Clone component repositories (if needed)
- Checkout specified versions
- Build Bazel targets
- Run tests

### 5. Run Tests

```bash
meta test --env dev
```

Runs:
- Component unit tests
- Contract tests (when implemented)
- End-to-end feature tests (when implemented)

### 6. Execute Commands

```bash
# Run a command in a specific component
meta exec "pytest tests/" --component agent-core

# Run a command in all components
meta exec "bazel build //..." --all
```

## Manifest Files

### `manifests/components.yaml`

Defines all components:
- Repository URL
- Version
- Type (bazel, docker, python, npm)
- Build target (for Bazel)

### `manifests/features.yaml`

Defines features that compose components:
- Component dependencies
- Contracts between components
- Policies (rate limiting, compliance, etc.)

### `manifests/environments.yaml`

Defines environment-specific configurations:
- dev
- staging
- prod

## Example Workflow

```bash
# 1. Check current status
meta status --env dev

# 2. Validate system
meta validate --env dev

# 3. Plan changes for staging
meta plan --env staging

# 4. Apply changes (dry run first)
meta apply --env staging --dry-run

# 5. Apply changes for real
meta apply --env staging

# 6. Run tests
meta test --env staging

# 7. Execute custom command
meta exec "bazel test //..." --component agent-core
```

## Next Steps

1. Update `manifests/components.yaml` with your actual component repositories
2. Customize `manifests/features.yaml` for your feature definitions
3. Configure `manifests/environments.yaml` for your environments
4. Implement contract validation logic in `meta/commands/validate.py`
5. Add feature test execution in `meta/commands/test.py`


