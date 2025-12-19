# Phase 15-20 Documentation

## Overview

This document provides comprehensive documentation for Phases 15-20 of the meta-repo CLI, covering collaboration & workflow, deployment & operations, advanced monitoring, compliance & governance, and OS-level declarative management.

## Phase 15: Collaboration & Workflow

### Component Templates Library

The templates library allows you to create, share, and reuse component templates.

**Commands:**
- `meta templates list` - List available templates
- `meta templates install <name> <source>` - Install a template
- `meta templates search <query>` - Search for templates
- `meta templates publish <name>` - Publish template to registry

**Example:**
```bash
# Install a template
meta templates install python-service ./templates/python-service

# Search for templates
meta templates search "python"

# List all templates
meta templates list
```

### Component Notifications

Configure notifications for component events.

**Commands:**
- `meta notify setup --email <email> --slack <webhook>` - Setup notification channels
- `meta notify subscribe <component> <events>` - Subscribe to component events
- `meta notify test` - Test notification setup

**Example:**
```bash
# Setup notifications
meta notify setup --email admin@example.com --slack https://hooks.slack.com/...

# Subscribe to component events
meta notify subscribe frontend-service "update,failure,success"
```

### Component Aliases

Create aliases for components and environments.

**Commands:**
- `meta alias create <type> <alias> <target>` - Create an alias
- `meta alias delete <type> <alias>` - Delete an alias
- `meta alias list [--type <type>]` - List aliases
- `meta alias resolve <type> <alias>` - Resolve an alias

**Example:**
```bash
# Create component alias
meta alias create comp web frontend-service

# Create environment alias
meta alias create env prod production

# List all aliases
meta alias list
```

### Enhanced Component Search

Search components with advanced filtering.

**Commands:**
- `meta search components <query> [--type <name|type|repo|tag|all>]` - Search components
- `meta search deps <component>` - Find components that depend on a component
- `meta search version <pattern>` - Search by version pattern

**Example:**
```bash
# Search by name
meta search components "frontend"

# Find dependents
meta search deps backend-api

# Search by version
meta search version "v1\\.\\d+\\.\\d+"
```

### Component History

Track component action history.

**Commands:**
- `meta history show [component] [--limit <n>] [--action <action>]` - Show history
- `meta history clear [component]` - Clear history

**Example:**
```bash
# Show component history
meta history show frontend-service

# Show all history
meta history show

# Clear history
meta history clear frontend-service
```

## Phase 16: Deployment & Operations

### Component Deployment Strategies

Deploy components with various strategies.

**Commands:**
- `meta deploy component <name> <version> [--strategy <strategy>] [--canary <pct>] [--instances <n>]` - Deploy component
- `meta deploy promote <component> [--percentage <pct>]` - Promote canary deployment
- `meta deploy rollback <component> [--version <v>]` - Rollback deployment

**Strategies:**
- `immediate` - Immediate deployment (default)
- `blue-green` - Blue-green deployment
- `canary` - Canary deployment
- `rolling` - Rolling deployment

**Example:**
```bash
# Blue-green deployment
meta deploy component frontend-service v2.0.0 --strategy blue-green --instances 2

# Canary deployment
meta deploy component api-service v1.5.0 --strategy canary --canary 10 --instances 10

# Promote canary
meta deploy promote api-service --percentage 50
```

### Component Sync

Synchronize components to desired versions.

**Commands:**
- `meta sync component <name> [--env <env>]` - Sync a component
- `meta sync all [--env <env>]` - Sync all components
- `meta sync env <env>` - Sync all components in environment

**Example:**
```bash
# Sync single component
meta sync component frontend-service --env prod

# Sync all components
meta sync all --env prod
```

### Component Review

Review components for issues and recommendations.

**Commands:**
- `meta review component <name>` - Review a component
- `meta review all` - Review all components

**Example:**
```bash
# Review component
meta review component frontend-service

# Review all
meta review all
```

## Phase 17: Advanced Monitoring

### Component Monitoring Integration

Integrate with monitoring systems.

**Commands:**
- `meta monitor setup <provider> [--endpoint <url>] [--api-key <key>]` - Setup monitoring provider
- `meta monitor register <component> [--metrics <list>]` - Register component
- `meta monitor metrics <component> [--range <time>]` - Get metrics
- `meta monitor alerts [--component <name>]` - Get alerts

**Providers:**
- `prometheus` - Prometheus
- `datadog` - Datadog
- `newrelic` - New Relic

**Example:**
```bash
# Setup Prometheus
meta monitor setup prometheus --endpoint http://prometheus:9090

# Register component
meta monitor register frontend-service --metrics "cpu,memory,requests"

# Get metrics
meta monitor metrics frontend-service --range 1h
```

### Component Optimization

Analyze and optimize components.

**Commands:**
- `meta optimize analyze [component]` - Analyze component(s)
- `meta optimize apply <component> [--auto-fix]` - Apply optimizations

**Example:**
```bash
# Analyze component
meta optimize analyze frontend-service

# Apply optimizations
meta optimize apply frontend-service --auto-fix
```

## Phase 18: Compliance & Governance

### Component Compliance Reporting

Generate compliance reports.

**Commands:**
- `meta compliance report [--component <name>] [--format <json|yaml>] [--output <file>]` - Generate report

**Example:**
```bash
# Generate compliance report
meta compliance report

# Export to file
meta compliance report --format json --output compliance.json
```

### Component Versioning Strategies

Manage versioning strategies.

**Commands:**
- `meta versioning bump <component> [--level <major|minor|patch>] [--strategy <strategy>]` - Bump version
- `meta versioning generate <component> [--strategy <strategy>]` - Generate version

**Strategies:**
- `semantic` - Semantic versioning (major.minor.patch)
- `calendar` - Calendar versioning (YYYY.MM.DD)
- `snapshot` - Snapshot versioning (commit SHA)
- `custom` - Custom versioning

**Example:**
```bash
# Bump patch version
meta versioning bump frontend-service --level patch

# Generate calendar version
meta versioning generate api-service --strategy calendar
```

## Phase 20: OS-Level Declarative Management

### OS Configuration Manifest

Define OS configuration declaratively.

**Commands:**
- `meta os init [--manifest <file>]` - Initialize OS manifest
- `meta os add <package|service|user|file> <name> [options]` - Add items
- `meta os validate [--manifest <file>]` - Validate manifest

**Example:**
```bash
# Initialize manifest
meta os init

# Add package
meta os add package nginx --version latest

# Add service
meta os add service nginx --enabled

# Add user
meta os add user appuser --groups www-data --home /home/appuser

# Add file
meta os add file /etc/nginx/nginx.conf --content "user www-data;" --mode 0644

# Validate
meta os validate
```

### OS Provisioning

Provision OS from manifest.

**Commands:**
- `meta os provision [--manifest <file>] [--provider <provider>] [--target <host>] [--dry-run]` - Provision OS

**Providers:**
- `ansible` - Ansible (default)
- `terraform` - Terraform
- `cloud-init` - Cloud-init
- `shell` - Shell scripts

**Example:**
```bash
# Provision with Ansible
meta os provision --provider ansible --target server.example.com

# Dry run
meta os provision --dry-run
```

### OS State Management

Manage OS state.

**Commands:**
- `meta os state capture [--manifest <file>]` - Capture current state
- `meta os state compare [--manifest <file>]` - Compare with manifest
- `meta os state restore` - Restore from state

**Example:**
```bash
# Capture state
meta os state capture

# Compare with manifest
meta os state compare

# Restore state
meta os state restore
```

### OS Build & Deploy

Build OS images and deploy.

**Commands:**
- `meta os build [--manifest <file>] [--output <name>] [--format <format>]` - Build image
- `meta os deploy [--manifest <file>] [--target <target>] [--method <method>]` - Deploy OS

**Formats:**
- `docker` - Docker image (default)
- `iso` - ISO image
- `qcow2` - QCOW2 image

**Methods:**
- `provision` - Provisioning (default)
- `image` - Image deployment
- `container` - Container deployment

**Example:**
```bash
# Build Docker image
meta os build --format docker --output my-os:latest

# Deploy via container
meta os deploy --method container --target local
```

### OS Monitoring

Monitor OS metrics and compliance.

**Commands:**
- `meta os monitor metrics` - Collect OS metrics
- `meta os monitor compliance [--manifest <file>]` - Check compliance

**Example:**
```bash
# Collect metrics
meta os monitor metrics

# Check compliance
meta os monitor compliance
```

## Best Practices

1. **Templates**: Create reusable templates for common component patterns
2. **Notifications**: Subscribe to critical component events
3. **Deployment**: Use canary or blue-green for production deployments
4. **Monitoring**: Integrate with your existing monitoring infrastructure
5. **Compliance**: Run compliance reports regularly
6. **OS Management**: Use declarative OS configuration for consistency

## Troubleshooting

### Templates not found
- Check template installation path
- Verify template index exists

### Deployment failures
- Check component health before deployment
- Verify target environment configuration

### OS provisioning errors
- Validate manifest before provisioning
- Check provider-specific requirements (Ansible, Terraform, etc.)

## See Also

- [Quick Reference](./QUICK_REFERENCE.md) - Command reference
- [Getting Started](./GETTING_STARTED.md) - Getting started guide
- [Testing](./TESTING.md) - Testing guide


