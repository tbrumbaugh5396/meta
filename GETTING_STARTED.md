# Getting Started with Meta-Repos

## Overview

Your system has been migrated to a hierarchical meta-repo architecture with 3 levels:

1. **Level 0: platform-meta** - Foundation infrastructure
2. **Level 1: scraping-platform-meta** - Scraping and agent system
3. **Level 2: gambling-platform-meta** - Application and UIs

## Quick Start

### 1. Navigate to a Meta-Repo

```bash
cd platform-meta          # Level 0
cd scraping-platform-meta # Level 1
cd gambling-platform-meta  # Level 2
```

### 2. Validate the System

```bash
meta validate
```

This checks:
- Component versions
- Dependency relationships (including component dependencies)
- Manifest validity
- Contract compliance
- No circular dependencies

### 3. Plan Changes

```bash
meta plan --env dev
```

Shows what would change if you apply updates.

### 4. Generate Lock File (Recommended)

```bash
meta lock
```

Generates a lock file with exact commit SHAs for reproducible builds. Commit this file to Git.

### 5. Apply Changes

```bash
meta apply --env dev
meta apply --locked  # Use lock file for exact commits
```

Applies component updates to the target environment. The `--locked` flag ensures you use exact commit SHAs from the lock file.

**Note:** Package manager dependencies (npm, pip, cargo, go) are automatically installed during `meta apply`. Use `--skip-packages` to skip this step.

## Working with Components

### View All Components

```bash
# In any meta-repo
cat manifests/components.yaml
```

### Update a Component Version

1. Edit `manifests/components.yaml`
2. Update the version number
3. Run `meta validate` to check (validates dependencies)
4. Run `meta plan` to see changes
5. Run `meta lock` to regenerate lock file
6. Run `meta apply --locked` to apply with exact commits

### Add a New Component

1. Create component repository
2. Add to `manifests/components.yaml`
3. Define dependencies using `depends_on`:
   ```yaml
   components:
     my-component:
       repo: "git@github.com:org/my-component.git"
       version: "v1.0.0"
       type: "bazel"
       depends_on:
         - dependency-component-1
         - dependency-component-2
   ```
4. Run `meta validate` (checks dependencies exist and no cycles)
5. Run `meta lock` to update lock file
6. Run `meta apply --locked` to check out component

## Component Development

### Create a New Component

1. Copy `component-template/` directory
2. Rename to your component name
3. Update `setup.py` with component details
4. Add code to `src/`
5. Define contracts in `contracts/`
6. Write tests in `tests/`

### Component Structure

```
component-name/
├── src/component_name/    # Source code
├── contracts/             # Interface contracts
├── tests/                # Tests
├── BUILD.bazel           # Bazel build
├── setup.py              # Python package
└── README.md             # Documentation
```

## Feature Development

### Define a Feature

Create a YAML file in `features/`:

```yaml
feature:
  name: my-feature
  description: "Feature description"
  components:
    - component-1
    - component-2
  contracts:
    - "component-1.output -> component-2.input"
  policies:
    - type: "rate-limit"
      max_requests_per_minute: 30
```

### Use Features

Features are automatically validated when you run:
```bash
meta validate
```

## Environment Management

### Define Environments

Edit `manifests/environments.yaml`:

```yaml
environments:
  dev:
    component-1: "dev"
    component-2: "dev"
  prod:
    component-1: "prod"
    component-2: "prod"
```

### Switch Environments

```bash
meta apply --env prod
```

## Lock Files and Reproducible Builds

### Generate Lock File

```bash
meta lock
```

This creates `manifests/components.lock.yaml` with exact commit SHAs for all components. This ensures reproducible builds across environments.

### Validate Lock File

```bash
meta lock validate
```

Validates that the lock file matches your current `components.yaml` manifest.

### Use Lock File

```bash
meta apply --locked
```

Applies components using exact commit SHAs from the lock file instead of version tags.

**Best Practice:** Always commit lock files to Git and use `--locked` in CI/CD pipelines.

## Package Management

The meta CLI automatically detects and installs package manager dependencies:

- **npm** - Detects `package.json`, runs `npm ci` or `npm install`
- **pip** - Detects `requirements.txt` or `setup.py`, runs `pip install`
- **cargo** - Detects `Cargo.toml`, runs `cargo build`
- **go** - Detects `go.mod`, runs `go mod download`

This happens automatically during `meta apply`. Use `--skip-packages` to skip installation.

## Testing

### Run Component Tests

```bash
# In component directory
bazel test //...
```

### Run System Tests

```bash
# In meta-repo directory
meta test
```

### Run Contract Tests

```bash
# In component directory
bazel test //:contract_tests
```

### Run Meta CLI Tests

```bash
# In meta-repo directory
pytest tests/
```

## Troubleshooting

### Component Not Found

```bash
# Check if component is in manifests
cat manifests/components.yaml | grep component-name

# Check if component is checked out
ls -la components/component-name
```

### Dependency Issues

```bash
# Validate dependencies (checks for missing deps and cycles)
meta validate

# Check dependency graph
cat manifests/components.yaml

# Check component dependencies
cat manifests/components.yaml | grep -A 5 "depends_on"
```

The `meta validate` command now automatically:
- Checks that all `depends_on` entries reference existing components
- Detects circular dependencies
- Validates dependency order

### Import Errors

1. Check component is checked out
2. Verify import paths match component structure
3. Check dependencies are installed

## Best Practices

1. **Always validate** before applying changes
2. **Use lock files** for reproducible builds (`meta lock` + `meta apply --locked`)
3. **Define dependencies** explicitly in `depends_on` fields
4. **Use semantic versioning** for components
5. **Define contracts** for all interfaces
6. **Write tests** for components
7. **Document** component usage
8. **Keep features declarative** (YAML, not code)
9. **Commit lock files** to Git for team consistency
10. **Use `--locked` in CI/CD** for production deployments

## Next Steps

1. Review `ARCHITECTURE.md` for system overview
2. Check `COMPONENT_INVENTORY.md` for component list
3. Read `PHASE1_ENHANCEMENTS.md` for lock files, dependency validation, and package management
4. Read `META-REPO.md` for governance
5. See `MIGRATION_PLAN.md` for migration details

