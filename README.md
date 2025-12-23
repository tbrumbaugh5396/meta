# Meta-Repo CLI Tool

A powerful command-line tool for managing hierarchical meta-repository architectures. The `meta` CLI provides comprehensive capabilities for orchestrating multi-repository projects, managing dependencies, visualizing relationships, and automating common development workflows.

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Introduction](#introduction)
- [Key Features](#key-features)
- [Governance](#governance)
- [Quick Start](#quick-start)
- [Environments](#environments)
- [Component Status](#component-status)
- [Complete Command Reference](#complete-command-reference)
- [Examples](#examples)
- [Next Steps](#next-steps)

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
            /    |     \
       [Mono]  [Poly]  [Meta]
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

- **Dual modes**: Reference mode (orchestration) and Vendored mode (Linus-safe materialization)
- **Changeset system**: Atomic cross-repo operations via changesets (see [Changeset System](./docs/CHANGESET_SYSTEM.md))
- **Comprehensive tooling**: CLI that provides monorepo-like ergonomics while preserving architectural boundaries
- **Integration testing**: System-level validation ensures all components work together
- **Environment management**: Dev, staging, and production configurations with version pinning
- **CI/CD integration**: Local testing of GitHub Actions workflows with `act`

#### Reference Mode vs Vendored Mode

The system supports two modes:

- **Reference Mode** (default): Components are git repositories. Provides flexibility and live updates, but requires external dependencies.
- **Vendored Mode**: Components are copied into meta-repo as source code. Provides Linus-safe self-contained commits, true atomicity, and no external dependencies. See [Vendored Mode](./docs/VENDORED_MODE.md) for details.

[↑ Back to Table of Contents](#table-of-contents)

## Key Features

### 1. **Changeset System for Atomic Operations**
   - Group commits across multiple repos into logical transactions
   - Atomic rollback across all repos in a changeset
   - Bisect to find which changeset introduced a bug
   - Full audit trail of cross-repo changes
   - See [Changeset System](./docs/CHANGESET_SYSTEM.md) for details

### 2. **Unified Git Operations**
   - Execute git commands across all repositories
   - Support for meta-repos and components
   - Changeset integration for atomic commits
   - Parallel execution (planned)

### 4. **Dependency Graph Visualization**
   - Multiple output formats (text, DOT, Mermaid)
   - Recursive traversal with depth control
   - Component promotion candidate analysis
   - Export to PDF/PNG/SVG
   - Full meta-repo dependency graphs

### 5. **Repository Management**
   - Batch updates (add, commit, push)
   - Status tracking across all repos
   - Selective updates (meta-repos only, components only)
   - Changeset-aware commits

### 6. **Package Management**
   - System-wide package installation
   - Python package management
   - Declarative manifests
   - Environment-specific dependencies

### 7. **Isolation & Reproducibility**
   - Virtual environment support
   - Docker containerization
   - Component-specific dependencies
   - Lock files for exact version pinning

### 8. **CI/CD Integration**
   - Local testing of GitHub Actions with `act`
   - Workflow and job testing
   - Environment-specific test runs
   - See [CI/CD Testing](#cicd-testing) section

### 9. **Environment Management**
   - Multiple environments (dev, staging, prod)
   - Environment-specific component versions
   - Lock files per environment
   - Environment promotion workflows

### 10. **Validation & Testing**
   - System-level validation
   - Dependency conflict detection
   - Component health checks
   - Integration test orchestration

### 11. **Advanced Features**
   - Component discovery and search
   - Dependency analysis and visualization
   - Rollback and recovery
   - Health monitoring
   - Analytics and metrics

[↑ Back to Table of Contents](#table-of-contents)

## Governance

### Purpose

This repository exists to **coordinate components, not to implement business logic**.

The meta-repo acts as a control plane that:
- Orchestrates multiple independent component repositories
- Enforces system-level invariants and correctness
- Defines features as declarative compositions of components
- Manages environment-specific configurations
- Provides system-level testing and validation

### Core Principles

#### 1. No Business Logic

**This repo orchestrates components, does not implement them.**

- Business logic belongs in component repositories
- This repo only contains:
  - Orchestration code (how components work together)
  - Feature definitions (declarative YAML/JSON)
  - System-level tests
  - CI/CD pipelines
  - Environment configurations

#### 2. Versioned Dependencies

**All components must be versioned and pinned.**

- Components are referenced by version in `manifests/components.yaml`
- Version changes require explicit updates
- System tests must pass before version bumps
- Rollback is always possible

#### 3. Declarative Features

**Features are YAML/JSON, not code.**

- Features define *what* components compose, not *how*
- Feature logic lives in components, not here
- Features can be added/modified without touching component code
- Features are environment-aware

#### 4. Interface Stability

**Component interfaces must be stable before extraction.**

- Components expose stable APIs (OpenAPI, gRPC, typed interfaces)
- Breaking changes require version bumps
- Contract tests validate interface compatibility
- Backward compatibility is maintained

#### 5. One-Way Dependencies

**Dependencies flow: Meta-Repo → Components (never reverse).**

- Meta-repo depends on components
- Components never depend on meta-repo
- Components can depend on other components (declared in features)
- No circular dependencies allowed

### Repository Structure

```
meta-repo/
├── meta/                    # CLI tool for meta-repo management
├── manifests/                # Declarative definitions
│   ├── components.yaml      # Component registry
│   ├── features.yaml        # Feature compositions
│   └── environments.yaml    # Environment configs
├── orchestration/           # Orchestration logic (stays here)
├── features/                # Feature definitions (declarative)
├── services/                # Service composition (thin layer)
├── interfaces/               # API layer (orchestration glue)
├── presentation/             # UI applications
├── environments/             # Environment configs
├── ci/                      # System-level CI
└── tests/                   # System-level tests
```

### Component Lifecycle

#### Adding a Component

1. **Define the component** in `manifests/components.yaml`:
   ```yaml
   components:
     my-component:
       repo: "git@github.com:org/my-component.git"
       version: "v1.0.0"
       type: "bazel"
       build_target: "//my_component:all"
   ```

2. **Validate the component**:
   ```bash
   meta validate --env dev
   ```

3. **Plan the addition**:
   ```bash
   meta plan --env dev
   ```

4. **Apply the component**:
   ```bash
   meta apply --env dev
   ```

5. **Test the integration**:
   ```bash
   meta test --env dev
   ```

#### Updating a Component

1. Update version in `manifests/components.yaml`
2. Run `meta plan` to see changes
3. Run `meta apply` to update
4. Run `meta test` to verify

#### Removing a Component

1. Remove from `manifests/components.yaml`
2. Remove from any features that reference it
3. Run `meta validate` to check for broken references
4. Remove component directory if needed

### Feature Definitions

Features are declarative compositions of components:

```yaml
features:
  my-feature:
    description: "What this feature does"
    components:
      - component-a
      - component-b
    contracts:
      - "component-a.output -> component-b.input"
    policies:
      - type: "rate-limit"
        max_requests_per_minute: 30
```

Features:
- Compose components (don't implement logic)
- Define contracts between components
- Specify policies (rate limits, compliance, etc.)
- Can depend on other features

### Enforcement Rules

#### Automated Checks

The following are enforced via CI:

1. **No direct component imports** - Components must be consumed via packages/APIs
2. **Features must be declarative** - No complex logic in feature definitions
3. **Version bumps require tests** - System tests must pass before merging
4. **Dependency acyclicity** - No circular dependencies
5. **Contract validation** - Component contracts must be satisfied

#### Manual Reviews

The following require code review:

1. New component additions
2. Feature definitions
3. Environment configurations
4. Orchestration logic changes
5. System test additions

### Testing Strategy

#### Tier 1: Component Tests (in component repos)
- Unit tests
- Component-specific integration tests
- Fast, deterministic
- Required to pass before publish

#### Tier 2: Contract Tests (in meta-repo)
- Validate interfaces between components
- Run on version bumps
- Catch breaking changes early

#### Tier 3: System Tests (in meta-repo)
- End-to-end feature tests
- Realistic data
- Failure-mode validation
- Performance tests

### Migration Guidelines

When extracting a capability from this repo to a component:

1. **Freeze the interface** - Define explicit inputs/outputs
2. **Write contract tests** - Validate the interface
3. **Create component repo** - Copy code to new repo
4. **Publish versioned artifact** - Make it available
5. **Update meta-repo** - Replace local code with dependency
6. **Run system tests** - Verify everything still works

### Common Mistakes to Avoid

❌ **Don't add business logic to meta-repo**
- Logic belongs in components
- Meta-repo only orchestrates

❌ **Don't create circular dependencies**
- Components can't depend on meta-repo
- Features can't create cycles

❌ **Don't skip versioning**
- Always pin component versions
- Never use "latest" in production

❌ **Don't mix concerns**
- Keep orchestration separate from implementation
- Keep features declarative

❌ **Don't break interfaces**
- Maintain backward compatibility
- Version breaking changes

### Decision Framework

If you're unsure whether something belongs in meta-repo or a component:

**Ask: "Can this be tested independently?"**
- Yes → It's a component
- No → It might be orchestration (or needs refactoring)

**Ask: "Does this compose other things?"**
- Yes → It's a feature (declarative)
- No → It might be a component

**Ask: "Does this enforce system correctness?"**
- Yes → It belongs in meta-repo
- No → It belongs in a component

**Remember: Correctness lives where invariants are enforced, not where features are defined.**

[↑ Back to Table of Contents](#table-of-contents)

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

[↑ Back to Table of Contents](#table-of-contents)

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

[↑ Back to Table of Contents](#table-of-contents)

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

[↑ Back to Table of Contents](#table-of-contents)

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

# Commit with changeset ID
meta git commit -m "Update feature" --changeset abc12345 --component agent-core
```

### Changeset Operations

#### `meta changeset`
Manage changesets for atomic cross-repo operations.

```bash
# Create a new changeset
meta changeset create "Description of change"

# Show changeset details
meta changeset show <changeset-id>

# List all changesets
meta changeset list [--limit N] [--status STATUS]

# Show current in-progress changeset
meta changeset current

# Finalize a changeset
meta changeset finalize [--id CHANGESET-ID]

# Rollback a changeset across all repos
meta changeset rollback <changeset-id> [--dry-run]

# Bisect to find breaking changeset
meta changeset bisect --start ID --end ID --test "COMMAND"
```

**Git Integration:**
```bash
# Commit with changeset ID
meta git commit -m "Message" --changeset <changeset-id> [--component COMPONENT]

# Lock file with changeset
meta lock --changeset <changeset-id>
```

See [Changeset System](./docs/CHANGESET_SYSTEM.md) for complete documentation.

### Vendor Operations (Linus-Safe Mode)

#### `meta vendor`
Vendor components into meta-repo for Linus-safe materialization with comprehensive safety features.

**Enable Vendored Mode:**
```yaml
# manifests/components.yaml
meta:
  mode: "vendored"  # Enable vendored mode

components:
  agent-core:
    repo: "git@github.com:org/agent-core.git"
    version: "v1.2.3"
```

**Basic Commands:**
```bash
# Import a single component
meta vendor import-component <component-name>

# Import all components
meta vendor import-all

# Force re-import (updates to new version)
meta vendor import-all --force

# Check vendor status
meta vendor status
```

**Enhanced Conversion Commands:**
```bash
# Convert with all safety features (recommended)
meta vendor convert vendored \
  --dry-run \              # Preview changes first
  --backup \               # Create backup (default)
  --atomic \               # All-or-nothing (default)
  --check-secrets \        # Security check (default)
  --verify                 # Verify after (default)

# Convert with continue-on-error
meta vendor convert vendored --continue-on-error

# Convert with specific options
meta vendor convert vendored \
  --fail-on-secrets \      # Fail if secrets detected
  --changeset abc12345 \   # Track in changeset
  --no-respect-gitignore   # Include all files

# Convert to reference mode
meta vendor convert reference
```

**Safety & Recovery Commands:**
```bash
# Verify conversion success
meta vendor verify

# Create manual backup
meta vendor backup --name my-backup

# Restore from backup
meta vendor restore my-backup

# List available backups
meta vendor list-backups

# Resume interrupted conversion
meta vendor resume

# Resume from specific checkpoint
meta vendor resume --checkpoint checkpoint-123

# List conversion checkpoints
meta vendor list-checkpoints
```

**Production Release Workflow:**
```bash
# Production release (converts to vendored with semantic versions)
meta vendor release --env prod --version v1.0.0
```

**Complete Workflow Example:**
```bash
# 1. Preview conversion (dry-run)
meta vendor convert vendored --dry-run

# 2. Convert with all safety features
meta vendor convert vendored \
  --backup \
  --atomic \
  --check-secrets \
  --verify \
  --changeset abc12345

# 3. If interrupted, resume
meta vendor resume

# 4. Verify conversion
meta vendor verify

# 5. If needed, restore from backup
meta vendor restore backup_20240115_120000
```

**Enhanced Features:**
- ✅ **Pre-conversion validation** - Validates prerequisites automatically
- ✅ **Dry-run mode** - Preview changes without making them
- ✅ **Continue-on-error** - Continue converting other components if one fails
- ✅ **Dependency-aware ordering** - Converts in correct dependency order
- ✅ **Secret detection** - Scans for API keys, passwords, tokens
- ✅ **Automatic backup** - Creates backup before conversion
- ✅ **Atomic transactions** - All-or-nothing conversion with rollback
- ✅ **File filtering** - Respects .gitignore patterns
- ✅ **Network resilience** - Automatic retry with exponential backoff
- ✅ **Conversion resume** - Resume from checkpoint after interruption
- ✅ **Changeset integration** - Track conversions in changesets
- ✅ **Semantic version validation** - Ensures production-ready versions
- ✅ **Conversion verification** - Verifies conversion success

See [Vendored Mode](./docs/VENDORED_MODE.md) and [Vendor Enhancements](./docs/VENDOR_ENHANCEMENTS.md) for complete documentation.

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
# Generate lock file
meta lock [--env ENV] [--changeset CHANGESET-ID]

# Validate lock file
meta lock validate [--env ENV]

# Promote lock file between environments
meta lock promote <from-env> <to-env>

# Compare lock files
meta lock compare [--env1 ENV1] [--env2 ENV2]
```

Options:
- `--env ENV`: Environment to generate lock file for
- `--changeset CHANGESET-ID`: Associate lock file generation with a changeset
- `--validate`: Validate lock file after generation

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

#### `meta search`
Search for components.

```bash
# Search components
meta search components <query> [--type TYPE]

# Search dependencies
meta search deps <component>
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
# Analyze repository structure
meta migrate analyze <path> [--output FILE]

# Generate migration plan
meta migrate plan <source> <target> [--output FILE]

# Execute migration
meta migrate execute <plan-file> [--dry-run]
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
meta exec <command> [--component COMPONENT] [--all] [--parallel]
```

Examples:
```bash
# Run tests in a component
meta exec pytest tests/ --component agent-core

# Run build command in all components
meta exec bazel build //... --all

# Run npm install
meta exec npm install --component scraper-capabilities
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

### Component Synchronization

#### `meta sync`
Synchronize components.

```bash
# Sync a component
meta sync component <component> [--env ENV]

# Sync all components
meta sync all [--env ENV]
```

### Component History

#### `meta history`
View component history.

```bash
# Show history for a component
meta history show [--component COMPONENT] [--limit N] [--action ACTION]

# Clear history
meta history clear [--component COMPONENT]
```

### Component Optimization

#### `meta optimize`
Analyze and optimize components.

```bash
# Analyze component
meta optimize analyze [COMPONENT]

# Apply optimizations
meta optimize apply <component> [--auto-fix]
```

### Component Monitoring

#### `meta monitor`
Monitor component status.

```bash
meta monitor [--component COMPONENT]
```

### Component Review

#### `meta review`
Review component changes.

```bash
meta review [--component COMPONENT]
```

### Component Deployment

#### `meta deploy`
Deploy components.

```bash
meta deploy [--component COMPONENT] [--env ENV]
```

### Component Templates

#### `meta templates`
Manage component templates.

```bash
meta templates list
meta templates create <name>
```

### Component Aliases

#### `meta alias`
Manage component aliases.

```bash
meta alias list
meta alias add <alias> <component>
meta alias remove <alias>
```

### Component Benchmarking

#### `meta benchmark`
Benchmark components.

```bash
meta benchmark [--component COMPONENT]
```

### Component Cost Analysis

#### `meta cost`
Analyze component costs.

```bash
meta cost [--component COMPONENT]
```

### Component Compliance

#### `meta compliance`
Check compliance.

```bash
meta compliance [--component COMPONENT]
```

### Component Versioning

#### `meta versioning`
Manage component versioning strategies.

```bash
meta versioning [--component COMPONENT]
```

### Component Notifications

#### `meta notify`
Configure notifications.

```bash
meta notify [--component COMPONENT] [--events EVENTS]
```

### Component Publishing

#### `meta publish`
Publish components or releases.

```bash
meta publish [--component COMPONENT] [--version VERSION]
```

### Component Documentation

#### `meta docs`
Generate documentation.

```bash
# Generate documentation
meta docs generate [--component COMPONENT] [--all] [--format FORMAT]

# Serve documentation
meta docs serve [--component COMPONENT] [--port PORT]
```

### Component API

#### `meta api`
Manage component APIs.

```bash
meta api [--component COMPONENT]
```

### Component Dependency Injection

#### `meta di`
Manage dependency injection.

```bash
meta di [--component COMPONENT]
```

### Component Test Templates

#### `meta test-templates`
Manage test templates.

```bash
meta test-templates [--component COMPONENT]
```

### Component Licensing

#### `meta license`
Manage licenses.

```bash
meta license [--component COMPONENT]
```

### Component Garbage Collection

#### `meta gc`
Garbage collect unused artifacts.

```bash
meta gc [--component COMPONENT]
```

### Component Store

#### `meta store`
Manage content-addressed store.

```bash
# Add to store
meta store add <component> --source PATH [--remote URL]

# Get from store
meta store get <component> <hash> --target PATH

# List store entries
meta store list [--component COMPONENT]
```

### Component Cache

#### `meta cache`
Manage build cache.

```bash
meta cache [--component COMPONENT]
```

### Component Release

#### `meta release`
Manage releases.

```bash
meta release [--component COMPONENT]
```

### Component Changelog

#### `meta changelog`
Generate changelogs.

```bash
meta changelog [--component COMPONENT]
```

### Component Security

#### `meta security`
Security operations.

```bash
meta security [--component COMPONENT]
```

### OS Management

#### `meta os`
OS-level management.

```bash
meta os [--component COMPONENT]
```

[↑ Back to Table of Contents](#table-of-contents)

## Examples

### Example 1: Atomic Cross-Repo Changes with Changesets

```bash
# Create a changeset for a feature
meta changeset create "Add authentication feature"

# Make changes across multiple repos
meta git commit -m "Add auth interface" --changeset abc12345 --component agent-core
meta git commit -m "Implement auth logic" --changeset abc12345 --component detector-core

# Update lock file
meta lock --changeset abc12345

# Finalize the changeset
meta changeset finalize abc12345

# If something breaks, rollback the entire changeset
meta changeset rollback abc12345
```

### Example 2: Check Status and Update All Repos

```bash
# Check current status
meta status

# Update all repositories
meta update all --message "Update dependencies" --push

# Or update selectively
meta update all --meta-repos-only
meta update all --components-only
```

### Example 3: Visualize Dependencies

```bash
# Generate Mermaid diagram
meta graph full --format mermaid --show-components

# Export to PDF
meta graph full --format mermaid --export pdf --image-width 2400

# Find promotion candidates
meta graph promotion-candidates --min-dependents 2

# Show component dependencies
meta graph component agent-core --format mermaid
```

### Example 4: Git Operations Across Repos

```bash
# Check status of all components
meta git status --all

# Commit changes in specific component with changeset
meta git commit -m "Add feature" --component agent-core --changeset abc12345

# Push all changes
meta git push --all

# View log for meta-repo
meta git log --oneline -n 10 --meta-repo
```

### Example 5: Install Dependencies

```bash
# Install from manifest
meta install system-packages

# Install Python packages
meta install python requests pytest

# Install system tools
meta install system git docker --manager brew
```

### Example 6: Test CI/CD Locally

```bash
# List available workflows
meta cicd test --list

# Test a specific job
meta cicd test --job validate --event workflow_dispatch --env dev

# Test entire workflow
meta cicd test --workflow .github/workflows/meta-apply.yml

# Test with custom options
meta cicd test --job validate --progress --pull-images
```

### Example 7: Environment Management

```bash
# Validate dev environment
meta validate --env dev

# Generate lock file for staging
meta lock --env staging

# Apply changes to production
meta apply --env prod --locked

# Compare environments
meta diff --env1 dev --env2 staging
```

### Example 8: Dependency Management

```bash
# Analyze dependencies
meta deps --component agent-core

# Detect conflicts
meta conflicts

# Generate lock file
meta lock --env dev

# Validate lock file
meta lock validate --env dev
```

### Example 9: Component Management

```bash
# Discover components
meta discover

# Search for components
meta search components "auth"

# Get component info
meta info --component agent-core

# Scaffold new component
meta scaffold component my-component --type bazel
```

### Example 10: Health and Monitoring

```bash
# Check health of all components
meta health --all

# View metrics
meta metrics --component agent-core

# Monitor system
meta monitor --component agent-core
```

[↑ Back to Table of Contents](#table-of-contents)

## Documentation

The meta-repo CLI documentation is organized by functional systems:

### Core Systems

- **[Lock Files and Reproducibility](./docs/LOCK_FILES_AND_REPRODUCIBILITY.md)** - Lock files, multi-environment locks, promotion, and comparison
- **[Dependency Management](./docs/DEPENDENCY_MANAGEMENT.md)** - Dependency validation, conflict resolution, and visualization
- **[Package Management](./docs/PACKAGE_MANAGEMENT.md)** - Package manager support, security scanning, and license checking
- **[Caching and Storage](./docs/CACHING_AND_STORAGE.md)** - Local/remote cache, content-addressed storage, and garbage collection
- **[Rollback and Recovery](./docs/ROLLBACK_AND_RECOVERY.md)** - Rollback commands, snapshots, and recovery workflows
- **[Health and Monitoring](./docs/HEALTH_AND_MONITORING.md)** - Health checks and monitoring capabilities

### Operations and Workflows

- **[Component Operations](./docs/COMPONENT_OPERATIONS.md)** - Apply, validate, plan, and status commands
- **[Vendored Mode](./docs/VENDORED_MODE.md)** - Linus-safe materialization mode with conversion capabilities
- **[Changeset System](./docs/CHANGESET_SYSTEM.md)** - Atomic cross-repo operations
- **[Configuration Management](./docs/CONFIGURATION_MANAGEMENT.md)** - Project and global configuration
- **[CI/CD Integration](./docs/CI_CD_GUIDE.md)** - CI/CD integration examples and workflows

### Developer Experience

- **[Developer Experience](./docs/DEVELOPER_EXPERIENCE.md)** - Scaffolding, auto-completion, component info, and debugging
- **[Isolation and System Packages](./docs/ISOLATION_AND_SYSTEM_PACKAGES.md)** - Component isolation and system package management
- **[Testing](./docs/TESTING.md)** - Testing guide and test infrastructure

### Reference

- **[Architecture](./docs/ARCHITECTURE.md)** - System architecture and component structure
- **[Getting Started](./docs/GETTING_STARTED.md)** - Quick start guide
- **[Commands](./docs/COMMANDS.md)** - Complete command reference
- **[Quick Reference](./docs/QUICK_REFERENCE.md)** - Quick command reference

[↑ Back to Table of Contents](#table-of-contents)

## Next Steps

1. Review the [Getting Started Guide](./docs/GETTING_STARTED.md)
2. Read the [Architecture Overview](./docs/ARCHITECTURE.md)
3. Explore [Component Operations](./docs/COMPONENT_OPERATIONS.md) for daily workflows
4. Use the [Quick Reference](./docs/QUICK_REFERENCE.md) for commands

[↑ Back to Table of Contents](#table-of-contents)
