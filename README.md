# Meta-Repo CLI Tool

A powerful command-line tool for managing hierarchical meta-repository architectures. The `meta` CLI provides comprehensive capabilities for orchestrating multi-repository projects, managing dependencies, visualizing relationships, and automating common development workflows.

## Table of Contents

- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Quick Links](#quick-links)
- [Environments](#environments)
- [Component Status](#component-status)
- [Complete Command Reference](#complete-command-reference)
- [What Was Created](#what-was-created)
- [Key Features](#key-features)
- [Examples](#examples)
- [Next Steps](#next-steps)
- [Status](#status)

## Introduction

### Understanding Repository Architectures

Modern software systems can be organized using different repository architectures, each with distinct trade-offs. The meta-repo approach combines the best aspects of monorepos and polyrepos while providing system-level orchestration.

#### Core Repository Types

| Type | Definition | Strengths | Weaknesses |
|------|------------|----------|------------|
| **Monorepo** | All code in a single repository | Atomic commits, fast refactors, simple CI, unified history | Harder ownership boundaries, less modularity, limited permissions control |
| **Polyrepo** | Each subsystem in its own repository | Clear ownership, modularity, independent versioning, permissions control | Harder cross-repo refactors, more complex CI, coordination required |
| **Meta-repo** | Aggregates multiple repos (mono, poly, or other meta) | System-level orchestration, integration tests, virtual monorepo experience, flexible boundaries | Requires tooling and CI investment, Git-level atomicity is simulated |

#### The Meta-Repo Advantage

Meta-repos act as a **superset** of monorepo and polyrepo capabilities:

```
          [Meta-Repo]
          /    |    \
       [Mono] [Poly] [Meta]
```

**Key Benefits:**

1. **Virtual Monorepo Experience**: With proper tooling, developers get monorepo-like workflows (fast refactors, unified search, atomic changes via changesets) while maintaining polyrepo benefits (modularity, ownership, permissions).

2. **Flexible Boundaries**: You can operate in "mono mode" when velocity matters, and "poly mode" when you need to enforce modularity, contracts, and independent releases.

3. **System-Level Correctness**: Meta-repos provide integration testing, dependency validation, and atomic changesets that ensure the entire system works together correctly.

4. **Architectural Discipline**: The friction of cross-repo changes encourages explicit contracts, stable interfaces, and better system design—mirroring how distributed systems actually work.

#### Tooling Effects

| Capability | Monorepo | Polyrepo | Meta-Repo + Tooling |
|------------|----------|----------|---------------------|
| Developer workflow | ✅ | ⚠️ | ✅ (virtual monorepo) |
| Atomic commits | ✅ | ❌ | ✅ (simulated via changesets) |
| Global refactors | ✅ | ⚠️ | ✅ (coordinated via tooling) |
| CI simplicity | ✅ | ⚠️ | ✅ (meta-repo CI orchestrates) |
| Ownership / permissions | Low | High | High |
| Modular boundaries | Soft | Hard | Hard + enforced |

#### Why Meta-Repos?

Meta-repos provide **flexibility**—the "best of both worlds":

- **Mono mode**: Fast refactors, debugging, local testing—works whenever you need it
- **Poly mode**: Enforce modularity, contracts, releases, and permissions—works whenever beneficial  
- **Meta mode**: Integrates everything, guarantees system-level correctness, enforces atomic changes via changesets, enables nested orchestration

This flexibility is why meta-repo + tooling is a superset of monorepo capabilities. You can always use it as a monorepo, but you gain modularity, ownership, and enforcement that a pure monorepo cannot provide.

#### Key Takeaways

- **Meta-repo = superset of mono + poly**: Combines the strengths of both approaches
- **Tooling + changesets**: Simulate atomic commits and global refactors across repos
- **Developer experience**: Can be monorepo-like, even across multiple repositories
- **Architecture enforcement**: Modularity and contracts are enforced without sacrificing workflow
- **Dynamic trade-offs**: Teams can dial between speed, discipline, and autonomy as needed

### This Meta-Repo System

This implementation provides a complete meta-repo solution with:

- **Hierarchical architecture**: Three levels (platform → scraping → gambling) for clear separation of concerns
- **Changeset system**: Atomic cross-repo operations via changesets (see [Changeset System](./CHANGESET_SYSTEM.md))
- **Comprehensive tooling**: CLI that provides monorepo-like ergonomics while preserving architectural boundaries
- **Integration testing**: System-level validation ensures all components work together
- **Environment management**: Dev, staging, and production configurations with version pinning

## 🎉 Migration Complete!

This project has been successfully migrated to a hierarchical meta-repo architecture.

## Quick Start

```bash
# Install the meta CLI
pip install -e .

# Check system status
meta status

# Validate configuration
meta validate --env dev

# Apply changes
meta apply --env dev
```

## Quick Links

- [Summary](./SUMMARY.md) - Executive summary
- [Architecture](./ARCHITECTURE.md) - System architecture
- [Component Inventory](./COMPONENT_INVENTORY.md) - Complete component list
- [Getting Started](./GETTING_STARTED.md) - How to use meta-repos
- [Quick Reference](./QUICK_REFERENCE.md) - Command reference
- [Phase 1 Enhancements](./PHASE1_ENHANCEMENTS.md) - Lock files, dependency validation, package management
- [Phase 2 Enhancements](./PHASE2_ENHANCEMENTS.md) - Multi-env locks, security, caching, content-addressed storage
- [Phase 3 Enhancements](./PHASE3_ENHANCEMENTS.md) - Rollback, remote cache/store, progress indicators
- [Phase 4 Enhancements](./PHASE4_ENHANCEMENTS.md) - Health checks, CI/CD integration, configuration management
- [Phase 15-20 Complete](./PHASE15_20_COMPLETE.md) - Collaboration, deployment, monitoring, compliance, OS-level management
- [Migration Plan](./MIGRATION_PLAN.md) - Detailed migration plan
- [Verification](./VERIFICATION_CHECKLIST.md) - Verification checklist

## Structure

```
meta-repo/
├── META-REPO.md              # Governance document
├── MIGRATION_PLAN.md          # Complete migration plan
├── MIGRATION_STATUS.md        # Status tracking
├── ARCHITECTURE.md            # Architecture overview
├── COMPONENT_INVENTORY.md     # Component inventory
├── INTERFACE_CONTRACTS.md     # Interface contracts
├── QUICK_REFERENCE.md         # Quick reference guide
├── GETTING_STARTED.md         # Getting started guide
└── VERIFICATION_CHECKLIST.md  # Verification checklist
```

## Environments

The meta-repo system supports multiple environments, each with its own component versions and configurations. Environments are defined in `manifests/environments.yaml` within each meta-repo.

### Standard Environments

- **`dev`** (Development)
  - Used for local development and testing
  - Typically uses the latest or development versions of components
  - Allows rapid iteration and experimentation
  - Default environment for most commands

- **`staging`** (Staging)
  - Pre-production environment for integration testing
  - Uses stable versions of components
  - Mirrors production configuration for validation
  - Used for final testing before production deployment

- **`prod`** (Production)
  - Live production environment
  - Uses pinned, stable versions of components
  - Requires explicit version management
  - Changes should be carefully validated before deployment

### Environment Configuration

Each environment specifies which version of each component should be used:

```yaml
environments:
  dev:
    agent-core: "dev"
    detector-core: "dev"
    infrastructure-primitives: "dev"
  
  staging:
    agent-core: "staging"
    detector-core: "staging"
    infrastructure-primitives: "staging"
  
  prod:
    agent-core: "v1.2.3"
    detector-core: "v2.0.1"
    infrastructure-primitives: "v3.1.0"
```

You can specify:
- Branch names (e.g., `"dev"`, `"main"`, `"feature-x"`)
- Tag names (e.g., `"v1.2.3"`, `"release-2024-01"`)
- Commit hashes (e.g., `"abc123def"`)

### Using Environments

Most commands accept an `--env` or `-e` option to specify the environment:

```bash
# Check status for dev environment (default)
meta status

# Check status for staging environment
meta status --env staging

# Apply changes to production
meta apply --env prod

# Validate production configuration
meta validate --env prod
```

### Managing Environments

You can manage environments using the `meta config environment` command:

```bash
# List all environments
meta config environment list

# Show details of an environment
meta config environment show <env-name>

# Add a new environment (defaults to using env-name as version for all components)
meta config environment add <env-name>

# Add environment by copying from existing
meta config environment add qa --from dev

# Add environment with specific component versions
meta config environment add qa --component agent-core:dev --component detector-core:v2.0.0

# Edit an environment (set specific component versions)
meta config environment edit <env-name> --component agent-core:v1.2.3

# Set all components in an environment to the same version
meta config environment edit <env-name> --set-all dev

# Delete an environment (cannot delete dev, staging, or prod)
meta config environment delete <env-name>

# Reset all environments to defaults (dev, staging, prod)
meta config environment reset
```

**Note**: The standard environments (`dev`, `staging`, `prod`) cannot be deleted, but can be reset to defaults using the `reset` command.

## Component Status

The `meta status` command displays the current state of all components in your meta-repo. Each component shows a status indicator that reflects its current state relative to the desired version for the selected environment.

### Status Indicators

| Symbol | Status | Meaning |
|--------|--------|---------|
| **✓** | Correct Version | Component is checked out at the correct version that matches the desired version for the current environment |
| **⚠** | Version Mismatch | Component is checked out, but at a different version than what's specified for the current environment |
| **○** | Not Checked Out | Component repository is not checked out locally (doesn't exist or isn't a git repository) |

### Understanding Status Output

When you run `meta status`, you'll see a table with the following columns:

- **Status**: Visual indicator (✓, ⚠, or ○)
- **Component**: Name of the component
- **Desired Version**: Version specified in the environment configuration
- **Current Version**: Currently checked out version (or "not checked out")
- **Type**: Component type (e.g., "service", "library", "infrastructure")

### Example Status Output

```
Status  Component                  Desired Version  Current Version  Type
✓       agent-core                dev              dev             service
⚠       detector-core             v2.0.1          v2.0.0          service
○       infrastructure-primitives  dev              not checked out library
```

### Resolving Status Issues

**Version Mismatch (⚠)**:
```bash
# Checkout the correct version
meta git checkout <desired-version> --component <component-name>

# Or use apply to sync all components
meta apply --env <env>
```

**Not Checked Out (○)**:
```bash
# Apply changes to checkout and setup the component
meta apply --env <env> --component <component-name>

# Or checkout manually
meta git checkout <desired-version> --component <component-name>
```

**Correct Version (✓)**:
- No action needed! The component is at the correct version.

## Complete Command Reference

### Core Commands

#### `meta status`
Show current system status for all components.

```bash
meta status [--env ENV]
```

Displays:
- Component status (✓ checked out, ○ not checked out, ⚠ version mismatch)
- Desired vs current versions
- Component types

#### `meta validate`
Validate meta-repo configuration and manifests.

```bash
meta validate [--env ENV]
```

#### `meta plan`
Generate an execution plan for applying changes.

```bash
meta plan [--env ENV] [--component COMPONENT]
```

#### `meta apply`
Apply changes to components (install, build, test).

```bash
meta apply [--env ENV] [--component COMPONENT] [--all] [--isolate]
```

Options:
- `--env ENV`: Environment to apply (default: dev)
- `--component COMPONENT`: Apply to specific component
- `--all`: Apply to all components
- `--isolate`: Set up isolated environment (venv/docker)

#### `meta test`
Run tests for components.

```bash
meta test [--env ENV] [--component COMPONENT]
```

### Git Operations

#### `meta git`
Execute git commands across meta-repos and components.

```bash
# General git command
meta git <git-command> [git-args...] [--component COMPONENT] [--all] [--meta-repo]

# Convenience subcommands
meta git status [--component COMPONENT] [--all] [--meta-repo]
meta git add [files...] [--component COMPONENT] [--all] [--meta-repo]
meta git commit -m "message" [--component COMPONENT] [--all] [--meta-repo]
meta git push [--component COMPONENT] [--all] [--meta-repo]
meta git pull [--component COMPONENT] [--all] [--meta-repo]
meta git log [git-log-options...] [--component COMPONENT] [--all] [--meta-repo]
meta git diff [git-diff-options...] [--component COMPONENT] [--all] [--meta-repo]
meta git branch [git-branch-options...] [--component COMPONENT] [--all] [--meta-repo]
meta git checkout [branch/tag] [--component COMPONENT] [--all] [--meta-repo]
```

Options:
- `--component COMPONENT` / `-c`: Run on specific component
- `--all` / `-a`: Run on all components
- `--meta-repo`: Run on meta-repo root
- `--parallel` / `-p`: Execute in parallel (not yet implemented)

Examples:
```bash
# Check status of all components
meta git status --all

# Commit changes in a specific component
meta git commit -m "Update feature" --component agent-core

# Push all changes
meta git push --all

# View log for meta-repo
meta git log --oneline -n 10 --meta-repo
```

### Repository Updates

#### `meta update`
Update all repositories with git operations (add, commit, push).

```bash
# Update all repositories
meta update all [--message MESSAGE] [--push/--no-push] [--remote REMOTE] [--branch BRANCH]

# Show status of all repositories
meta update status
```

Options:
- `--message MESSAGE` / `-m`: Commit message (default: "Update repositories")
- `--push` / `--no-push`: Push to remote after commit (default: true)
- `--remote REMOTE` / `-r`: Remote name (default: origin)
- `--branch BRANCH` / `-b`: Branch name (default: main)
- `--meta-repos-only`: Only update meta-repos
- `--components-only`: Only update component repos

Examples:
```bash
# Update all repos with custom message
meta update all --message "Refactor components" --push

# Update only meta-repos
meta update all --meta-repos-only

# Check status without committing
meta update status
```

### Package Management

#### `meta install`
Install system packages and dependencies.

```bash
# Install system packages from manifest
meta install system-packages [--manifest PATH]

# Install Python packages globally
meta install python <package1> [package2...] [--pip-path PATH]

# Install system packages using package manager
meta install system <package1> [package2...] [--manager MANAGER]
```

Examples:
```bash
# Install from system-packages.yaml
meta install system-packages

# Install Python packages
meta install python requests==2.31.0 pytest==7.4.0

# Install system tools
meta install system git docker bazel --manager brew
```

### Dependency Graph Visualization

#### `meta graph`
Visualize dependency relationships between components and meta-repos.

```bash
# Show graph for a specific component
meta graph component <component-name> [--format FORMAT] [--output FILE]

# Show graph for all components
meta graph all [--format FORMAT] [--output FILE]

# Show meta-repo dependency graph
meta graph meta-repo [--repo REPO] [--direction DIRECTION] [--format FORMAT] [--recursive] [--max-depth DEPTH]

# Show complete connected graph (parents, children, siblings)
meta graph full [--repo REPO] [--format FORMAT] [--max-depth DEPTH] [--unlimited] [--show-components] [--sort-repos SORT] [--export FORMAT]

# Identify components that could be promoted to meta-repos
meta graph promotion-candidates [--min-dependents N] [--min-component-dependents N] [--format FORMAT] [--output FILE]
```

**Graph Formats:**
- `text`: Human-readable text output (default)
- `dot`: Graphviz DOT format
- `mermaid`: Mermaid diagram format

**Graph Commands:**

1. **`meta graph component`**: Show dependencies for a specific component
   ```bash
   meta graph component agent-core --format mermaid
   ```

2. **`meta graph all`**: Show dependency graph for all components
   ```bash
   meta graph all --format dot --output graph.dot
   ```

3. **`meta graph meta-repo`**: Show which meta-repos use this one and which this one uses
   ```bash
   # Show dependencies (down)
   meta graph meta-repo --direction down --recursive
   
   # Show dependents (up)
   meta graph meta-repo --direction up --recursive
   
   # Show both
   meta graph meta-repo --direction both --recursive --max-depth 5
   ```

4. **`meta graph full`**: Complete connected graph with recursive expansion
   ```bash
   # Text output
   meta graph full --repo gambling-platform-meta
   
   # Mermaid with components shown
   meta graph full --show-components --format mermaid --sort-repos top
   
   # Export to PDF
   meta graph full --format mermaid --export pdf --image-width 2400 --image-height 1800
   
   # Unlimited depth traversal
   meta graph full --unlimited --show-components
   ```

   Options:
   - `--show-components` / `-c`: Show components as first-class nodes
   - `--sort-repos`: Sort repos by dependency count (`top`, `bottom`, `none`)
   - `--repo-color`: Color for meta-repos (default: green)
   - `--component-color`: Color for components (default: red)
   - `--component-level`: Place components at same level (`top`, `bottom`)
   - `--export`: Export Mermaid to image (`pdf`, `png`, `svg`)
   - `--unlimited` / `-u`: Unlimited traversal depth

5. **`meta graph promotion-candidates`**: Identify components that could become meta-repos
   ```bash
   # Default thresholds (2 meta-repo dependents OR 3 component dependents)
   meta graph promotion-candidates
   
   # Custom thresholds
   meta graph promotion-candidates --min-dependents 3 --min-component-dependents 5
   
   # Export to JSON
   meta graph promotion-candidates --output candidates.json
   ```

   This command analyzes components and suggests which ones might benefit from being promoted to their own meta-repos based on:
   - Number of meta-repos that depend on the component
   - Number of components that depend on it
   - Dependency complexity

### Dependency Management

#### `meta deps`
Analyze and manage component dependencies.

```bash
meta deps [--component COMPONENT] [--format FORMAT]
```

#### `meta conflicts`
Detect dependency conflicts.

```bash
meta conflicts [--component COMPONENT]
```

#### `meta lock`
Generate or update lock files.

```bash
meta lock [--env ENV] [--component COMPONENT]
```

### Rollback & Recovery

#### `meta rollback`
Rollback to a previous state.

```bash
meta rollback [--env ENV] [--component COMPONENT] [--to VERSION]
```

### Health & Monitoring

#### `meta health`
Check health status of components.

```bash
meta health [--env ENV] [--component COMPONENT]
```

#### `meta metrics`
View system metrics.

```bash
meta metrics [--component COMPONENT] [--format FORMAT]
```

### Configuration

#### `meta config`
Manage configuration settings.

```bash
meta config [get|set|list] [KEY] [VALUE]
```

### Scaffolding

#### `meta scaffold`
Generate component templates.

```bash
meta scaffold component <name> [--template TEMPLATE]
```

### Information & Discovery

#### `meta info`
Show information about components or meta-repo.

```bash
meta info [--component COMPONENT]
```

#### `meta discover`
Discover components and dependencies.

```bash
meta discover [--path PATH]
```

#### `meta compare`
Compare component versions or configurations.

```bash
meta compare [--component COMPONENT] [--env ENV]
```

#### `meta diff`
Show differences between versions or environments.

```bash
meta diff [--component COMPONENT] [--env1 ENV1] [--env2 ENV2]
```

### Advanced Features

#### `meta workspace`
Manage workspace settings.

```bash
meta workspace [init|list|switch] [NAME]
```

#### `meta interactive`
Launch interactive mode.

```bash
meta interactive
```

#### `meta publish`
Publish components or releases.

```bash
meta publish [--component COMPONENT] [--version VERSION]
```

#### `meta migrate`
Migrate components or configurations.

```bash
meta migrate [--from FROM] [--to TO]
```

#### `meta registry`
Manage component registry.

```bash
meta registry [list|add|remove] [COMPONENT]
```

#### `meta dashboard`
Launch web dashboard (if available).

```bash
meta dashboard [--port PORT]
```

### CI/CD Testing

#### `meta cicd test`
Test CI/CD pipelines locally using `act` (GitHub Actions runner).

```bash
# List available workflows and jobs
meta cicd test --list

# Test a specific workflow
meta cicd test --workflow .github/workflows/meta-apply.yml

# Test a specific job
meta cicd test --job validate

# Test with workflow_dispatch event and environment input
meta cicd test --event workflow_dispatch --env dev

# Dry run (see what would execute without running)
meta cicd test --dry-run

# Use custom secrets file
meta cicd test --secrets-file .secrets
```

**Prerequisites:**
- Install `act`: `brew install act` (macOS) or see https://github.com/nektos/act
- Docker must be running (act uses Docker containers)
- Optional: Create `.secrets` file for any required secrets

**Setup:**
```bash
# Get setup instructions and check prerequisites
meta cicd setup github
```

**Examples:**
```bash
# Test the validate job
meta cicd test --job validate

# Test the full apply workflow with staging environment
meta cicd test --workflow .github/workflows/meta-apply.yml --event workflow_dispatch --env staging

# List all available workflows
meta cicd test --list
```

#### `meta cicd setup`
Set up local testing environment for CI/CD providers.

```bash
# Setup for GitHub Actions (uses act)
meta cicd setup github

# Setup for GitLab CI
meta cicd setup gitlab

# Setup for Jenkins
meta cicd setup jenkins
```

### Security & Compliance

#### `meta audit`
Run security audits.

```bash
meta audit [--component COMPONENT]
```

#### `meta secrets`
Manage secrets.

```bash
meta secrets [list|get|set|delete] [KEY]
```

#### `meta policies`
Manage policies.

```bash
meta policies [list|apply|validate]
```

### Utilities

#### `meta exec`
Execute commands in component contexts.

```bash
meta exec <command> [--component COMPONENT] [--all]
```

#### `meta backup`
Create backups.

```bash
meta backup [--component COMPONENT] [--output PATH]
```

#### `meta updates`
Check for updates.

```bash
meta updates [--component COMPONENT]
```

#### `meta analytics`
View analytics data.

```bash
meta analytics [--component COMPONENT] [--format FORMAT]
```

#### `meta plugins`
Manage plugins.

```bash
meta plugins [list|install|remove] [PLUGIN]
```

#### `meta completion`
Generate shell completion scripts.

```bash
meta completion [bash|zsh|fish]
```

#### `meta help`
Show help for commands.

```bash
meta help [COMMAND]
```

#### `meta version`
Show CLI version.

```bash
meta version
```

## What Was Created

- **19 Component Repositories** - All extracted and structured
- **3 Meta-Repo Repositories** - Hierarchical organization
- **50+ Interface Contracts** - Stable interfaces defined
- **4 Feature Definitions** - Declarative feature YAMLs
- **Phase 1 Enhancements** - Lock files, dependency validation, package management
- **Phase 2 Enhancements** - Multi-environment locks, security scanning, caching, content-addressed storage
- **Phase 3 Enhancements** - Rollback command, remote cache/store (S3/GCS), progress indicators & parallel execution
- **Phase 4 Enhancements** - Health checks, CI/CD integration, configuration management
- **Comprehensive Documentation** - Complete guides and references

## Key Features

### 1. **Unified Git Operations**
   - Execute git commands across all repositories
   - Support for meta-repos and components
   - Parallel execution (planned)

### 2. **Dependency Graph Visualization**
   - Multiple output formats (text, DOT, Mermaid)
   - Recursive traversal with depth control
   - Component promotion candidate analysis
   - Export to PDF/PNG/SVG

### 3. **Repository Management**
   - Batch updates (add, commit, push)
   - Status tracking across all repos
   - Selective updates (meta-repos only, components only)

### 4. **Package Management**
   - System-wide package installation
   - Python package management
   - Declarative manifests

### 5. **Isolation & Reproducibility**
   - Virtual environment support
   - Docker containerization
   - Component-specific dependencies

## Examples

### Example 1: Check Status and Update All Repos

```bash
# Check current status
meta status

# Update all repositories
meta update all --message "Update dependencies" --push
```

### Example 2: Visualize Dependencies

```bash
# Generate Mermaid diagram
meta graph full --repo gambling-platform-meta --format mermaid --show-components

# Export to PDF
meta graph full --format mermaid --export pdf --image-width 2400

# Find promotion candidates
meta graph promotion-candidates --min-dependents 2
```

### Example 3: Git Operations Across Repos

```bash
# Check status of all components
meta git status --all

# Commit changes in specific component
meta git commit -m "Add feature" --component agent-core

# Push all changes
meta git push --all
```

### Example 4: Install Dependencies

```bash
# Install from manifest
meta install system-packages

# Install Python packages
meta install python requests pytest

# Install system tools
meta install system git docker --manager brew
```

## Next Steps

1. Review the [Getting Started Guide](./GETTING_STARTED.md)
2. Check the [Component Inventory](./COMPONENT_INVENTORY.md)
3. Read the [Architecture Overview](./ARCHITECTURE.md)
4. Use the [Quick Reference](./QUICK_REFERENCE.md) for commands

## Status

✅ **100% Complete** - All phases finished successfully

See [FINAL_STATUS.md](./FINAL_STATUS.md) for complete status.
