# Phase 1 Enhancements: Lock Files, Dependency Validation, and Package Management

## Overview

Phase 1 enhancements add three critical features to the meta-repo CLI:

1. **Lock Files** - Reproducible builds with exact commit SHAs
2. **Dependency Validation** - Ensures all component dependencies exist and are acyclic
3. **Package Manager Support** - Automatic installation of npm, pip, cargo, and go dependencies

## 1. Lock Files

### Purpose

Lock files ensure reproducible builds by pinning exact commit SHAs instead of just version tags. This prevents "works on my machine" issues and ensures all environments use identical code.

### Usage

#### Generate Lock File

```bash
meta lock
```

This generates `manifests/components.lock.yaml` with exact commit SHAs for all components.

#### Validate Lock File

```bash
meta lock validate
```

Validates that the lock file matches the current `components.yaml` manifest.

#### Use Lock File for Apply

```bash
meta apply --locked
```

Applies components using exact commit SHAs from the lock file instead of version tags.

### Lock File Format

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

### Best Practices

- **Commit lock files to Git** - Ensures team uses same versions
- **Regenerate after version updates** - Run `meta lock` after changing component versions
- **Use in CI/CD** - Always use `--locked` flag in production deployments
- **Validate in CI** - Add `meta lock validate` to your CI pipeline

## 2. Dependency Validation

### Purpose

Validates that:
- All component dependencies exist in the manifest
- No circular dependencies exist
- Components are applied in correct dependency order

### Usage

Dependency validation runs automatically during `meta validate`:

```bash
meta validate
```

This will:
1. Check that all `depends_on` entries reference existing components
2. Detect circular dependencies
3. Report any dependency errors

### Component Dependencies

Define dependencies in `manifests/components.yaml`:

```yaml
components:
  scraper-capabilities:
    repo: "git@github.com:yourorg/scraper-capabilities.git"
    version: "v3.0.1"
    type: "bazel"
    build_target: "//scraper_capabilities:all"
    depends_on:
      - infrastructure-primitives
      - agent-core
```

### Dependency Resolution

When applying components, they are automatically applied in dependency order:

```bash
meta apply
```

Components with no dependencies are applied first, followed by components that depend on them.

### Transitive Dependencies

Dependencies are resolved transitively. If `A` depends on `B`, and `B` depends on `C`, then `C` will be applied before `B`, and `B` before `A`.

## 3. Package Manager Support

### Purpose

Automatically detects and installs package manager dependencies (npm, pip, cargo, go) for components during `meta apply`.

### Supported Package Managers

- **npm** - Detects `package.json`, runs `npm ci` (if `package-lock.json` exists) or `npm install`
- **pip** - Detects `requirements.txt` or `setup.py`, runs `pip install`
- **cargo** - Detects `Cargo.toml`, runs `cargo build`
- **go** - Detects `go.mod`, runs `go mod download`

### Usage

Package installation happens automatically during `meta apply`:

```bash
meta apply
```

The CLI will:
1. Detect which package managers are needed for each component
2. Install dependencies in the correct order
3. Report success/failure for each package manager

### Skip Package Installation

To skip package installation (e.g., if dependencies are already installed):

```bash
meta apply --skip-packages
```

### Detection Logic

The CLI detects package managers by looking for specific files:

- `package.json` → npm
- `requirements.txt` or `setup.py` or `pyproject.toml` → pip
- `Cargo.toml` → cargo
- `go.mod` → go
- `Dockerfile` → docker (detected but not installed automatically)

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

## Integration

All three features work together:

1. **Lock files** ensure reproducible builds
2. **Dependency validation** ensures correct component order
3. **Package management** ensures component dependencies are installed

### Complete Workflow

```bash
# 1. Validate system (includes dependency validation)
meta validate

# 2. Generate lock file for reproducibility
meta lock

# 3. Apply components (uses lock file, validates dependencies, installs packages)
meta apply --locked

# 4. In CI/CD, always use locked mode
meta apply --locked --skip-packages  # Skip packages if pre-installed
```

## Files Added

- `meta/utils/lock.py` - Lock file generation and validation
- `meta/utils/dependencies.py` - Dependency resolution and validation
- `meta/utils/packages.py` - Package manager detection and installation
- `meta/commands/lock.py` - Lock file CLI command

## Files Modified

- `meta/utils/git.py` - Added `get_commit_sha()` and `get_commit_sha_for_ref()`
- `meta/commands/validate.py` - Added component dependency validation
- `meta/commands/apply.py` - Added `--locked` flag, dependency ordering, package installation
- `meta/cli.py` - Added `lock` command
- `meta/utils/__init__.py` - Exported new utilities

## Benefits

1. **Reproducibility** - Lock files ensure identical builds across environments
2. **Correctness** - Dependency validation prevents broken configurations
3. **Automation** - Package installation reduces manual setup steps
4. **Reliability** - Dependency ordering ensures components are built in correct order

## Next Steps

These Phase 1 enhancements provide a solid foundation. Future enhancements could include:

- Content-addressed storage (Nix-like)
- Advanced caching
- Garbage collection
- Multi-environment lock files

But for now, these three features provide significant value with minimal complexity.


