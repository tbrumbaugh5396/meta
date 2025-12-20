# Isolation and System Package Management

## Overview

The meta-repo CLI now supports:
1. **System-wide package management** - Declarative system and Python package installation
2. **Component isolation** - Virtual environments and containers for component isolation

## System Package Management

### Configuration

Create `manifests/system-packages.yaml`:

```yaml
system_packages:
  python:
    version: "3.11"  # Required Python version
  
  system_tools:
    - git
    - docker
    - bazel
  
  global_packages:
    pip:
      - name: black
        version: "23.0.0"
      - name: pytest
        version: "7.4.0"
```

### Installation

```bash
# Install all system packages from manifest
meta install system-packages

# Install only Python packages (skip system tools)
meta install system-packages --skip-system

# Install only system tools (skip Python packages)
meta install system-packages --skip-python

# Install specific Python packages
meta install python requests==2.31.0 typer==0.9.0

# Install specific system packages
meta install system git docker bazel
```

### Supported Package Managers

- **System**: `apt`, `brew`, `yum`, `dnf`, `pacman`, `choco`, `winget`
- **Python**: `pip` (global or in venv)

## Component Isolation

### Configuration

Add isolation config to component in `manifests/components.yaml`:

```yaml
components:
  scraper-capabilities:
    repo: "git@github.com:org/scraper-capabilities.git"
    version: "v3.0.1"
    type: "bazel"
    isolation:
      type: "venv"  # or "docker", "none"
      python_version: "3.11"
      requirements: "requirements.txt"  # Optional, defaults to requirements.txt
```

### Usage

```bash
# Apply with isolation (uses venv if configured)
meta apply --isolate

# Apply specific component with isolation
meta apply --component scraper-capabilities --isolate

# Apply all components with isolation
meta apply --all --isolate
```

### Virtual Environments

When `isolation.type: "venv"` is set:
- Creates `.meta/venvs/<component-name>/` virtual environment
- Installs component dependencies in the venv
- Runs component commands in the isolated environment

**Benefits:**
- Prevents version conflicts between components
- Ensures reproducible builds
- Clean separation of dependencies

### Docker Support

Docker isolation is available as `isolation.type: "docker"`:
- Builds Docker container for component (requires Dockerfile in component)
- Creates isolated container environment
- Full OS-level isolation

**Requirements:**
- Component must have a `Dockerfile`
- Docker must be installed and running

## Workflow Examples

### Complete Setup

```bash
# 1. Install system packages
meta install system-packages

# 2. Apply components with isolation
meta apply --isolate

# 3. Validate everything works
meta validate
```

### Development Workflow

```bash
# Work on component in isolated environment
meta apply --component my-component --isolate

# Run tests in component's venv
cd components/my-component
source ../../.meta/venvs/my-component/bin/activate
pytest
```

### CI/CD Workflow

```bash
# Install system dependencies
meta install system-packages --skip-system  # Skip system tools in CI

# Apply with isolation for reproducibility
meta apply --locked --isolate
```

## Best Practices

1. **Always use isolation in production** - Prevents version conflicts
2. **Lock system packages** - Version your system-packages.yaml
3. **Use venv for development** - Easier than Docker for local dev
4. **Use Docker for production** - Full isolation and reproducibility
5. **Document Python versions** - Specify in system-packages.yaml

## Troubleshooting

### Virtual Environment Not Created

```bash
# Check Python version
python3 --version

# Manually create venv
python3 -m venv .meta/venvs/component-name
```

### Package Installation Fails

```bash
# Check if package manager is available
which pip
which apt  # or brew, etc.

# Install manually to debug
pip install package==version
```

### Version Conflicts

Use isolation to prevent conflicts:
```bash
meta apply --isolate
```

This ensures each component has its own dependency environment.

