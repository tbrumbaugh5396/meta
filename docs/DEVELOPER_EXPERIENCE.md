# Developer Experience

## Overview

The meta-repo CLI provides comprehensive developer experience features to make working with meta-repos easier and more productive, including component scaffolding, auto-completion, component information, and enhanced debugging capabilities.

## Component Scaffolding

### Purpose

Quickly create new components with proper structure, templates, and boilerplate code.

### Usage

#### Create a New Component

```bash
# Create a Bazel component
meta scaffold component my-component --type bazel

# Create a Python component
meta scaffold component my-component --type python

# Create an npm component
meta scaffold component my-component --type npm
```

#### Options

- `--type` - Component type (bazel, python, npm)
- `--add-to-manifest` - Automatically add to `components.yaml`
- `--template` - Use custom template

### What It Creates

For a Bazel component:
```
components/my-component/
├── BUILD.bazel
├── WORKSPACE
├── src/
│   └── main/
│       └── my_component/
│           └── __init__.py
├── tests/
│   └── test_my_component.py
├── contracts/
│   └── interface.yaml
└── README.md
```

For a Python component:
```
components/my-component/
├── setup.py
├── pyproject.toml
├── requirements.txt
├── src/
│   └── my_component/
│       └── __init__.py
├── tests/
│   └── test_my_component.py
└── README.md
```

For an npm component:
```
components/my-component/
├── package.json
├── tsconfig.json
├── src/
│   └── index.ts
├── tests/
│   └── index.test.ts
└── README.md
```

### Benefits

- **Quick Start** - Create components in seconds
- **Consistent Structure** - All components follow same patterns
- **Best Practices** - Templates include best practices
- **Ready to Use** - Components are immediately buildable

## Auto-Completion

### Purpose

Enable shell auto-completion for faster command entry and fewer typos.

### Supported Shells

- **Bash** - Most common Linux/Mac shell
- **Zsh** - Default on macOS
- **Fish** - Modern shell with great UX

### Installation

```bash
# Install for your shell
meta completion install bash
meta completion install zsh
meta completion install fish
```

### Usage

After installation, you can use tab completion:

```bash
meta <TAB>
# Shows: apply, validate, plan, status, lock, ...

meta apply <TAB>
# Shows: --all, --component, --env, --locked, ...

meta apply --component <TAB>
# Shows: scraper-capabilities, agent-core, ...
```

### Benefits

- **Faster Commands** - Tab completion speeds up command entry
- **Fewer Typos** - Auto-completion prevents typos
- **Discoverability** - See available options as you type
- **Better UX** - Modern shell experience

## Component Information

### Purpose

Quickly view detailed information about components.

### Usage

```bash
# Show component info
meta info component scraper-capabilities

# Show info for all components
meta info --all
```

### Information Displayed

- Component name and version
- Repository URL
- Component type (bazel, python, npm, etc.)
- Build target
- Dependencies
- Health status
- Lock file sync status
- Package managers detected

### Example Output

```
Component: scraper-capabilities
  Version: v3.0.1
  Repository: git@github.com:org/scraper-capabilities.git
  Type: bazel
  Build Target: //scraper_capabilities:all
  Dependencies:
    - infrastructure-primitives
    - agent-core
  Health: ✓ Healthy
  Lock File: ✓ In sync
  Package Managers: npm, pip
```

### Benefits

- **Quick Reference** - See component details instantly
- **Dependency Visibility** - Understand component relationships
- **Health Status** - Check component health at a glance
- **Discovery** - Learn about components in your meta-repo

## Verbose and Debug Mode

### Purpose

Get detailed output for debugging and understanding what the CLI is doing.

### Usage

#### Verbose Mode

```bash
# Show detailed output
meta apply --all --verbose

# Verbose with specific component
meta apply --component scraper-capabilities --verbose
```

#### Debug Mode

```bash
# Show debug-level output
meta apply --all --debug

# Debug with specific command
meta validate --debug
```

### Output Levels

- **Normal** - Standard output (default)
- **Verbose** - Detailed output with more information
- **Debug** - Maximum detail including internal operations

### Benefits

- **Debugging** - Understand what's happening internally
- **Troubleshooting** - Diagnose issues more easily
- **Learning** - See how the CLI works
- **Transparency** - Full visibility into operations

## Interactive Mode

### Purpose

Interactive mode provides a guided experience for common operations.

### Usage

```bash
# Start interactive mode
meta interactive

# Interactive mode for specific command
meta apply --interactive
```

### Features

- **Guided Workflows** - Step-by-step guidance
- **Menu Navigation** - Easy selection of options
- **Context-Aware** - Shows relevant information
- **Help Integration** - Built-in help and examples

### Benefits

- **Easier Onboarding** - New users can learn quickly
- **Reduced Errors** - Guided workflows prevent mistakes
- **Better UX** - Interactive experience is more intuitive
- **Help Integration** - Built-in help and examples

## Component Discovery

### Purpose

Discover and explore components in your meta-repo.

### Usage

```bash
# Discover all components
meta discover components

# Discover components matching pattern
meta discover components --pattern "scraper*"

# Discover with details
meta discover components --detailed
```

### Benefits

- **Exploration** - Find components you didn't know about
- **Pattern Matching** - Search for components by pattern
- **Details** - See component information during discovery

## Enhanced Help System

### Purpose

Better help system with examples, interactive help, and command-specific documentation.

### Usage

```bash
# General help
meta help

# Command-specific help
meta help apply

# Examples
meta help examples

# Interactive help
meta help interactive
```

### Features

- **Command Examples** - Real-world usage examples
- **Interactive Help** - Guided help experience
- **Context-Sensitive** - Help relevant to current context
- **Search** - Search help content

### Benefits

- **Better Documentation** - More helpful than standard --help
- **Examples** - See real-world usage
- **Interactive** - Guided help experience
- **Discoverability** - Find features you didn't know about

## Integration

All developer experience features work together:

```bash
# 1. Scaffold a new component
meta scaffold component my-component --type bazel

# 2. Get info about it
meta info component my-component

# 3. Use auto-completion for commands
meta apply --component my-component<TAB>

# 4. Use verbose mode to see what's happening
meta apply --component my-component --verbose

# 5. Use interactive mode for complex operations
meta interactive
```

## Implementation Details

### Files

- `meta/utils/scaffold.py` - Component scaffolding
- `meta/commands/scaffold.py` - Scaffold commands
- `meta/utils/completion.py` - Auto-completion generation
- `meta/commands/completion.py` - Completion installation
- `meta/commands/info.py` - Component information
- `meta/utils/logger.py` - Enhanced logging (verbose/debug)

### Auto-Completion Generation

Auto-completion is generated dynamically based on:
- Available commands
- Command options
- Component names
- Environment names

### Scaffold Templates

Templates are stored in `meta/templates/`:
- `bazel/` - Bazel component template
- `python/` - Python component template
- `npm/` - npm component template

## Benefits Summary

1. **Productivity** - Scaffolding and auto-completion speed up development
2. **Discoverability** - Info and discovery help you understand your meta-repo
3. **Debugging** - Verbose and debug modes help troubleshoot issues
4. **Onboarding** - Interactive mode and help system make it easy to learn
5. **Consistency** - Scaffolding ensures all components follow same patterns

