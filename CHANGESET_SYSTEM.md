# Changeset System for Atomic Cross-Repo Operations

## Overview

The changeset system solves the "atomic authorship" problem in meta-repos by providing a way to group related commits across multiple repositories into a single logical transaction.

## What Problem Does It Solve?

In a monorepo, you can make a single atomic commit that spans multiple components. In a meta-repo, commits are in separate repositories, making it difficult to:

- Track which commits belong together
- Bisect to find which change introduced a bug
- Rollback related changes atomically
- Understand causality across repos

The changeset system provides these capabilities.

## Core Concepts

### Changeset

A changeset is a logical transaction that groups commits across multiple repositories:

- **ID**: Unique identifier (e.g., `abc12345`)
- **Description**: Human-readable description of the change
- **Status**: `in-progress`, `committed`, `failed`, or `rolled-back`
- **Repos**: List of commits in each repository that belong to this changeset

### Changeset Tracking

Changesets are stored in `.meta/changesets/`:
- Each changeset has a YAML file: `{changeset-id}.yaml`
- An index file tracks all changesets: `index.yaml`
- Changesets are version-controlled (committed to git)

## Usage

### 1. Create a Changeset

```bash
meta changeset create "Refactor authentication across components"
# Output: Created changeset: abc12345
```

### 2. Make Commits with Changeset ID

**Option A: Include in commit message**
```bash
meta git commit -m "Update auth interface [changeset:abc12345]" --component agent-core
```

**Option B: Use --changeset flag**
```bash
meta git commit -m "Update auth interface" --changeset abc12345 --component agent-core
```

**Option C: Auto-detect current changeset**
If you have an in-progress changeset, it will be used automatically:
```bash
meta changeset create "My change"
meta git commit -m "Update code" --component agent-core
# Automatically uses the current in-progress changeset
```

### 3. Track Lock File Updates

```bash
meta lock --changeset abc12345
```

### 4. Finalize Changeset

```bash
meta changeset finalize abc12345
# Or just:
meta changeset finalize  # Uses current in-progress changeset
```

### 5. View Changeset

```bash
meta changeset show abc12345
```

### 6. List Changesets

```bash
meta changeset list
meta changeset list --limit 10
meta changeset list --status committed
```

### 7. Rollback a Changeset

```bash
# Dry run first
meta changeset rollback abc12345 --dry-run

# Actually rollback
meta changeset rollback abc12345
```

This will:
- Revert commits in reverse dependency order
- Create revert commits in each repository
- Mark the changeset as `rolled-back`

### 8. Bisect to Find Breaking Changeset

```bash
meta changeset bisect --start abc12345 --end xyz78901 --test "meta test --all"
```

This performs a binary search across changesets to find which one introduced a bug.

## Complete Workflow Example

```bash
# 1. Create changeset
meta changeset create "Add feature X"

# Output: Created changeset: abc12345

# 2. Make changes in component A
cd ../agent-core
# ... make changes ...
meta git commit -m "Add feature X support [changeset:abc12345]"

# 3. Make changes in component B
cd ../detector-core
# ... make changes ...
meta git commit -m "Use feature X [changeset:abc12345]"

# 4. Update meta-repo lock file
cd ../gambling-platform-meta
meta lock --changeset abc12345
meta git commit -m "Update lock for feature X [changeset:abc12345]"

# 5. Finalize
meta changeset finalize abc12345

# 6. If something breaks later, rollback
meta changeset rollback abc12345
```

## Changeset File Format

```yaml
id: abc12345
timestamp: 2024-01-15T10:30:00Z
author: user@example.com
description: "Refactor authentication across agent-core and detector-core"
status: committed

repos:
  - name: agent-core
    repo: git@github.com:org/agent-core.git
    commit: a1b2c3d4e5f6
    branch: main
    message: "Update auth interface [changeset:abc12345]"
  
  - name: detector-core
    repo: git@github.com:org/detector-core.git
    commit: e4f5g6h7i8j9
    branch: main
    message: "Use new auth interface [changeset:abc12345]"
  
  - name: gambling-platform-meta
    repo: git@github.com:org/gambling-platform-meta.git
    commit: k1l2m3n4o5p6
    branch: main
    message: "Update lock file for auth refactor [changeset:abc12345]"

metadata:
  related_issues: ["#123", "#456"]
  environment: dev
```

## Benefits

1. **Atomic Semantics**: Group related commits across repos
2. **Better Bisecting**: Find which changeset introduced a bug
3. **Safer Rollbacks**: Roll back entire logical changes together
4. **Causality Tracking**: See which commits belong together
5. **History Preservation**: Full audit trail of cross-repo changes

## Limitations

1. **Not True Git Atomicity**: Still separate commits, but logically grouped
2. **Requires Discipline**: Developers must use changeset IDs
3. **Tooling Dependency**: Need the meta CLI to manage changesets

## Integration Points

- **Git Commits**: Automatically track commits with changeset IDs
- **Lock Files**: Track lock file updates in changesets
- **CI/CD**: Can validate that changesets are complete before merging
- **History**: Full audit trail of all cross-repo changes

## Commands Reference

```bash
# Create and manage
meta changeset create <description> [--author AUTHOR]
meta changeset show <changeset-id>
meta changeset list [--limit N] [--status STATUS]
meta changeset current
meta changeset finalize [--id CHANGESET-ID]

# Operations
meta changeset rollback <changeset-id> [--dry-run]
meta changeset bisect --start ID --end ID --test "COMMAND"

# Git integration
meta git commit -m "message" [--changeset ID] [--component COMPONENT]

# Lock file integration
meta lock [--changeset ID] [--env ENV]
```

## Future Enhancements

- Changeset validation in CI/CD
- Automatic changeset detection from commit messages
- Changeset dependencies
- Changeset merging
- Changeset templates
- Integration with issue trackers

