# Meta-Repo Quick Reference

## Component Locations

### Platform Components (Level 0)
- `infrastructure-primitives/` - Core infrastructure
- `observability-platform/` - Monitoring, logging, tracing
- `security-platform/` - RBAC, authentication, secrets
- `execution-runtime/` - Execution engine, message queue

### Scraping Components (Level 1)
- `agent-core/` - Agent intelligence
- `detector-core/` - Bot detection
- `scraper-capabilities/` - Web scraping
- `emulation-engine/` - Browser fingerprinting
- `parsing-engine/` - Data parsing
- `orchestration-engine/` - Orchestrator management
- `workflow-engine/` - Workflow execution
- `scraper-server/` - Cluster management
- `ai-coding-learner/` - Code analysis

### Application Components (Level 2)
- `betting-calculators/` - Betting calculations
- `social-platform/` - Social features
- `live-betting-engine/` - Live betting
- `fund-transfer-engine/` - Fund transfers
- `data-processing/` - Data processing
- `integrations/` - External integrations

## Phase 15-20 Commands

### Collaboration & Workflow
```bash
# Templates
meta templates list
meta templates install <name> <source>
meta templates search <query>

# Notifications
meta notify setup --email <email> --slack <webhook>
meta notify subscribe <component> <events>

# Aliases
meta alias create <type> <alias> <target>
meta alias list --type <type>

# Search
meta search components <query>
meta search deps <component>
meta search version <pattern>

# History
meta history show [component]
meta history clear [component]
```

### Deployment & Operations
```bash
# Deployment
meta deploy component <name> <version> --strategy <blue-green|canary|rolling>
meta deploy promote <component> --percentage <pct>
meta deploy rollback <component> [--version <v>]

# Sync
meta sync component <name> --env <env>
meta sync all --env <env>
meta sync env <env>

# Review
meta review component <name>
meta review all
```

### Monitoring & Optimization
```bash
# Monitoring
meta monitor setup <provider> --endpoint <url> --api-key <key>
meta monitor register <component> --metrics <list>
meta monitor metrics <component>
meta monitor alerts [--component <name>]

# Optimization
meta optimize analyze [component]
meta optimize apply <component> [--auto-fix]
```

### Compliance & Governance
```bash
# Compliance
meta compliance report [--component <name>] [--format <json|yaml>] [--output <file>]

# Versioning
meta versioning bump <component> [--level <major|minor|patch>] [--strategy <semantic|calendar|snapshot>]
meta versioning generate <component> [--strategy <strategy>]
```

### OS-Level Declarative Management
```bash
# OS Configuration
meta os init [--manifest <file>]
meta os add <package|service|user|file> <name> [options]
meta os validate [--manifest <file>]

# OS Provisioning
meta os provision [--manifest <file>] [--provider <ansible|terraform|cloud-init|shell>] [--target <host>] [--dry-run]

# OS State
meta os state capture [--manifest <file>]
meta os state compare [--manifest <file>]
meta os state restore

# OS Build & Deploy
meta os build [--manifest <file>] [--output <name>] [--format <docker|iso|qcow2>]
meta os deploy [--manifest <file>] [--target <target>] [--method <provision|image|container>]

# OS Monitoring
meta os monitor metrics
meta os monitor compliance [--manifest <file>]
```

## Meta-Repos

### Level 0: platform-meta
```bash
cd platform-meta
meta validate
meta plan --env dev
meta apply --env dev
```

### Level 1: scraping-platform-meta
```bash
cd scraping-platform-meta
meta validate
meta plan --env dev
meta apply --env dev
```

### Level 2: gambling-platform-meta
```bash
cd gambling-platform-meta
meta validate
meta plan --env dev
meta apply --env dev
```

## Common Commands

### Validate System
```bash
meta validate --env dev
```

### Plan Changes
```bash
meta plan --env dev
```

### Apply Changes
```bash
meta apply --env dev
meta apply --all  # Apply all components
meta apply --component <name>  # Apply specific component
meta apply --locked  # Use lock file for exact commit SHAs
meta apply --skip-packages  # Skip package manager installation
```

### Lock Files (Reproducible Builds)
```bash
meta lock  # Generate lock file with exact commit SHAs
meta lock --env dev  # Generate environment-specific lock file
meta lock validate  # Validate lock file matches manifest
meta lock promote dev staging  # Promote lock file between environments
meta lock compare dev prod  # Compare lock files
```

### Dependency Management
```bash
meta deps lock --all  # Generate package lock files
meta deps audit --all  # Scan for vulnerabilities
meta deps licenses --all  # Check licenses
meta deps graph --format dot  # Generate dependency graph
```

### Conflict Resolution
```bash
meta conflicts check  # Check for conflicts
meta conflicts resolve --strategy latest  # Resolve conflicts
meta conflicts recommend  # Get update recommendations
```

### Caching
```bash
meta cache build component --source path/  # Build and cache
meta cache get component --target path/  # Retrieve from cache
meta cache list  # List cache entries
meta cache stats  # Cache statistics
```

### Content-Addressed Store
```bash
meta store add component --source path/  # Add to store
meta store add component --source path/ --remote s3://bucket/store  # With S3
meta store query hash  # Query store
meta store get hash --target path/ --remote gs://bucket/store  # From GCS
meta store list  # List store entries
meta gc all  # Garbage collection
```

### Rollback
```bash
meta rollback component <name> --to-version v1.0.0  # Rollback to version
meta rollback component <name> --to-commit abc123  # Rollback to commit
meta rollback lock lock-file.yaml  # Rollback from lock file
meta rollback store <name> <hash>  # Rollback from store
meta rollback list  # List available targets
meta rollback snapshot  # Create snapshot
```

### Progress & Parallel Execution
```bash
meta apply --all --parallel --jobs 4  # Parallel execution
meta apply --all --no-progress  # Disable progress bar
```

### Health Checks
```bash
meta health --component scraper-capabilities  # Check single component
meta health --all --env staging  # Check all components
meta health --all --build --tests  # Include build and test checks
```

### Configuration
```bash
meta config get default_env  # Get config value
meta config set default_env staging  # Set config value
meta config init  # Initialize config file
meta config  # Show all config
```

### CI/CD Integration
See `.github/workflows/meta-apply.yml`, `.gitlab-ci.yml`, `Jenkinsfile`, etc.
See `CI_CD_GUIDE.md` for complete guide.

### Run Tests
```bash
meta test
```

### Execute Command Across Components
```bash
meta exec "pytest tests/" --all
meta exec "bazel build //..." --component <name>
```

## Component Structure

Each component follows this structure:
```
component-name/
├── src/
│   └── component_name/
├── contracts/
│   └── component_interface.py
├── tests/
│   ├── unit/
│   ├── contract/
│   └── integration/
├── BUILD.bazel
├── setup.py
├── WORKSPACE
└── README.md
```

## Dependency Flow

```
gambling-platform-meta
  └── scraping-platform-meta
      └── platform-meta
```

## Key Files

- `manifests/components.yaml` - Component definitions
- `manifests/components.lock.yaml` - Lock file with exact commit SHAs (generated)
- `manifests/features.yaml` - Feature definitions
- `manifests/environments.yaml` - Environment configs
- `contracts/*.py` - Interface contracts
- `README.md` - Component documentation

## Versioning

All components use semantic versioning:
- `v1.0.0` - Initial release
- `v1.1.0` - Minor update (backward compatible)
- `v2.0.0` - Major update (breaking changes)

## New Features

### Phase 1
- **Lock Files** - Reproducible builds with exact commit SHAs
- **Dependency Validation** - Automatic validation of component dependencies
- **Package Management** - Automatic npm/pip/cargo/go dependency installation

### Phase 2
- **Multi-Environment Lock Files** - Environment-specific lock files
- **Enhanced Package Management** - Security scanning, license checking, dependency graphs
- **Dependency Conflict Resolution** - Automatic conflict detection and resolution
- **Advanced Caching** - Build artifact caching
- **Content-Addressed Storage** - Nix-like store system

See [PHASE1_ENHANCEMENTS.md](./PHASE1_ENHANCEMENTS.md) and [PHASE2_ENHANCEMENTS.md](./PHASE2_ENHANCEMENTS.md) for details.

## Getting Help

- See `META-REPO.md` for governance
- See `PHASE1_ENHANCEMENTS.md` for new features
- See `MIGRATION_PLAN.md` for migration details
- See `ARCHITECTURE.md` for architecture overview
- See `COMPONENT_INVENTORY.md` for component list

