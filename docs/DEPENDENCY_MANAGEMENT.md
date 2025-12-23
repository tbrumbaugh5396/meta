# Dependency Management

## Overview

The meta-repo CLI provides comprehensive dependency management including validation, conflict resolution, and visualization to ensure your component dependencies are correct and well-understood.

## Dependency Validation

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

## Dependency Conflict Resolution

### Purpose

Detect and resolve dependency conflicts automatically using semantic versioning.

### Commands

#### Check for Conflicts

```bash
meta conflicts check
```

Detects:
- Version conflicts between components
- Incompatible dependency ranges
- Circular dependencies

#### Resolve Conflicts

```bash
meta conflicts resolve --strategy latest
meta conflicts resolve --strategy conservative
meta conflicts resolve --strategy first
meta conflicts resolve --strategy highest
```

Strategies:
- **latest** - Use latest compatible version
- **conservative** - Use lowest compatible version
- **first** - Use first requirement's version
- **highest** - Use highest version

#### Get Recommendations

```bash
meta conflicts recommend
```

Suggests dependency updates based on available versions.

### Semantic Version Support

Components can use version ranges in `depends_on`:

```yaml
components:
  my-component:
    depends_on:
      - "dependency-component:^1.0.0"  # Caret range
      - "other-component:~2.1.0"       # Tilde range
      - "another-component:>=3.0.0"   # Greater than or equal
```

### Benefits

- **Early Detection** - Catch conflicts before deployment
- **Automatic Resolution** - Resolve conflicts automatically
- **Flexibility** - Support version ranges
- **Recommendations** - Get update suggestions

## Dependency Visualization

### Purpose

Understand dependency relationships through visual graphs.

### Commands

#### Generate Dependency Graph

```bash
meta graph --format dot --output graph.dot
meta graph --format mermaid --output graph.mmd
meta graph --format text  # Text tree output
```

Generates dependency graphs in various formats:
- **DOT** - Graphviz format for visualization
- **Mermaid** - Mermaid diagram format
- **Text** - ASCII tree format

#### Component Dependency Graph

```bash
meta deps graph --component scraper-capabilities --format dot --output graph.dot
```

Generates a graph showing all dependencies for a specific component.

### Benefits

- **Visibility** - Understand dependency relationships
- **Documentation** - Visual representation of system architecture
- **Debugging** - Identify dependency issues visually

## Integration with Other Systems

### Lock Files

Dependency information is included in lock files, ensuring reproducible dependency resolution:

```yaml
components:
  scraper-capabilities:
    version: "v3.0.1"
    commit: "abc123..."
    depends_on:
      - infrastructure-primitives
      - agent-core
```

### Changesets

Dependency changes can be tracked in changesets:

```bash
meta changeset create "Update component dependencies"
meta git commit -m "Add new dependency" --changeset abc12345
```

### Apply Command

The `meta apply` command automatically respects dependency order:

```bash
meta apply --all
# Components are applied in dependency order automatically
```

## Complete Workflow

```bash
# 1. Validate dependencies
meta validate  # Includes dependency validation

# 2. Check for conflicts
meta conflicts check

# 3. Resolve conflicts if needed
meta conflicts resolve --strategy latest

# 4. Visualize dependencies
meta graph --format dot --output deps.dot

# 5. Apply with dependency ordering
meta apply --all  # Automatically respects dependencies
```

## Implementation Details

### Files

- `meta/utils/dependencies.py` - Dependency resolution and validation
- `meta/utils/conflicts.py` - Conflict detection and resolution
- `meta/utils/semver.py` - Semantic version parsing
- `meta/utils/dependency_graph.py` - Dependency graph visualization
- `meta/commands/conflicts.py` - Conflict resolution commands

### Dependency Resolution Algorithm

1. Build dependency graph from manifest
2. Detect cycles (circular dependencies)
3. Topological sort to determine order
4. Validate all dependencies exist
5. Apply components in resolved order

### Conflict Detection

Conflict detection checks:
1. Version conflicts between components
2. Incompatible version ranges
3. Missing dependencies
4. Circular dependencies

## Benefits

1. **Correctness** - Dependency validation prevents broken configurations
2. **Reliability** - Dependency ordering ensures components are built in correct order
3. **Early Detection** - Catch conflicts before deployment
4. **Visibility** - Understand system architecture through visualization
5. **Automation** - Automatic resolution and ordering

