# Meta-Repo CLI Commands Reference

All commands support options in any position (before or after other arguments).

## Command: `meta validate`

Validates system correctness. Now includes component dependency validation (checks for missing dependencies and circular dependencies).

**Options:**
- `--env, -e` - Environment to validate (default: "dev")
- `--manifests, -m` - Manifests directory (default: "manifests")
- `--skip-bazel` - Skip Bazel validation
- `--skip-git` - Skip Git validation

**What it validates:**
- Component versions
- Component dependencies (all `depends_on` entries exist)
- No circular dependencies
- Feature contracts
- Manifest validity

**Examples:**
```bash
meta validate --env staging
meta validate --env dev --skip-bazel --skip-git
meta validate --skip-bazel --env staging
```

---

## Command: `meta plan`

Shows planned changes before applying.

**Options:**
- `--env, -e` - Environment to plan for (default: "dev")
- `--manifests, -m` - Manifests directory (default: "manifests")
- `--component, -c` - Plan for specific component only

**Examples:**
```bash
meta plan --env staging
meta plan --env dev --component agent-core
meta plan --component agent-core --env staging
```

---

## Command: `meta apply`

Deploys or syncs components to target environment. Automatically installs package manager dependencies (npm, pip, cargo, go) and applies components in dependency order. Supports parallel execution and progress indicators.

**Options:**
- `--env, -e` - Environment to apply to (default: "dev")
- `--manifests, -m` - Manifests directory (default: "manifests")
- `--component, -c` - Apply for specific component only
- `--all, -a` - Apply all components (even unchanged ones)
- `--locked` - Use lock file for exact commit SHAs (recommended for production)
- `--lock-file, -l` - Lock file path (default: "manifests/components.lock.yaml")
- `--skip-packages` - Skip package manager dependency installation
- `--parallel, -p` - Apply components in parallel (respects dependency order)
- `--jobs, -j` - Number of parallel jobs (default: 4)
- `--progress/--no-progress` - Show/hide progress bar (default: show)
- `--dry-run` - Show what would be done without making changes

**Examples:**
```bash
meta apply --env staging
meta apply --env dev --component agent-core
meta apply --all --parallel --jobs 4  # Parallel execution with progress
meta apply --all --no-progress  # Disable progress bar
meta apply --locked  # Use lock file for reproducible builds
meta apply --locked --skip-packages  # Use lock file, skip package installation
meta apply --component agent-core --dry-run --env staging
```

**Note:** Components are automatically applied in dependency order. Package manager dependencies are detected and installed automatically. Parallel execution respects dependency order by grouping independent components.

---

## Command: `meta test`

Runs system-level tests.

**Options:**
- `--env, -e` - Environment to test (default: "dev")
- `--manifests, -m` - Manifests directory (default: "manifests")
- `--component, -c` - Test specific component only
- `--feature, -f` - Test specific feature only
- `--skip-unit` - Skip unit tests
- `--skip-contract` - Skip contract tests
- `--skip-e2e` - Skip end-to-end tests

**Examples:**
```bash
meta test --env staging
meta test --env dev --component agent-core
meta test --component agent-core --skip-unit --env staging
```

---

## Command: `meta exec`

Executes commands across components. **Supports options before OR after the command.**

**Options:**
- `--component, -c` - Execute for specific component
- `--all, -a` - Execute for all components
- `--manifests, -m` - Manifests directory (default: "manifests")
- `--parallel, -p` - Execute in parallel (not yet implemented)

**Examples:**
```bash
# Options after command (natural CLI pattern)
meta exec pytest tests/ --component agent-core
meta exec bazel build //... --all
meta exec npm install --component scraper-capabilities

# Options before command (also works)
meta exec --component agent-core "pytest tests/"
meta exec --all "bazel build //..."
```

---

## Command: `meta status`

Shows current system status.

**Options:**
- `--env, -e` - Environment to check (default: "dev")

**Examples:**
```bash
meta status --env dev
meta status --env staging
```

---

## Command: `meta lock`

Generates and validates lock files for reproducible builds.

**Subcommands:**
- `meta lock` - Generate lock file with exact commit SHAs
- `meta lock validate` - Validate lock file matches manifest

**Options:**
- `--manifests, -m` - Manifests directory (default: "manifests")
- `--lock-file, -l` - Lock file path (default: "manifests/components.lock.yaml")
- `--validate` - Validate lock file after generation

**Examples:**
```bash
meta lock  # Generate lock file
meta lock --validate  # Generate and validate
meta lock validate  # Validate existing lock file
meta lock --lock-file custom.lock.yaml  # Use custom lock file path
```

**Note:** Lock files pin exact commit SHAs instead of version tags, ensuring reproducible builds. Always commit lock files to Git.

---

## Command: `meta deps`

Manage component dependencies (package locks, security, licenses, graphs).

**Subcommands:**
- `meta deps lock` - Generate package lock files
- `meta deps audit` - Scan for security vulnerabilities
- `meta deps licenses` - Check license compliance
- `meta deps graph` - Generate dependency graphs

**Examples:**
```bash
meta deps lock --all
meta deps audit --component scraper-capabilities
meta deps licenses --allowed "MIT,Apache-2.0"
meta deps graph --format dot --output graph.dot
```

---

## Command: `meta conflicts`

Detect and resolve dependency conflicts.

**Subcommands:**
- `meta conflicts check` - Check for conflicts
- `meta conflicts resolve` - Resolve conflicts automatically
- `meta conflicts recommend` - Get update recommendations

**Examples:**
```bash
meta conflicts check
meta conflicts resolve --strategy latest
meta conflicts recommend
```

---

## Command: `meta cache`

Manage build cache. Supports remote cache (S3, GCS) for sharing builds across machines.

**Subcommands:**
- `meta cache build` - Build and cache artifact
- `meta cache get` - Retrieve from cache
- `meta cache invalidate` - Invalidate cache entries
- `meta cache list` - List cache entries
- `meta cache stats` - Show cache statistics

**Options:**
- `--remote, -r` - Remote cache URL (s3://bucket or gs://bucket)

**Examples:**
```bash
meta cache build component --source path/
meta cache build component --source path/ --remote s3://my-bucket/cache
meta cache get component --target path/ --remote gs://my-bucket/cache
meta cache invalidate --all
meta cache stats
```

---

## Command: `meta store`

Manage content-addressed store. Supports remote store (S3, GCS) for sharing builds.

**Subcommands:**
- `meta store add` - Add artifact to store
- `meta store query` - Query store by hash
- `meta store get` - Retrieve from store
- `meta store list` - List store entries
- `meta store stats` - Show store statistics

**Options:**
- `--remote, -r` - Remote store URL (s3://bucket or gs://bucket)

**Examples:**
```bash
meta store add component --source path/
meta store add component --source path/ --remote s3://my-bucket/store
meta store query abc123def456...
meta store get abc123... --target output/ --remote gs://my-bucket/store
meta store stats
```

---

## Command: `meta gc`

Garbage collection for store and cache.

**Subcommands:**
- `meta gc store` - Collect store garbage
- `meta gc cache` - Collect cache garbage
- `meta gc all` - Collect all garbage

**Examples:**
```bash
meta gc store
meta gc cache --max-age 30
meta gc all --dry-run
```

---

## Command: `meta rollback`

Rollback components to previous states.

**Subcommands:**
- `meta rollback component` - Rollback specific component
- `meta rollback lock` - Rollback from lock file
- `meta rollback store` - Rollback from content-addressed store
- `meta rollback list` - List available rollback targets
- `meta rollback snapshot` - Create rollback snapshot

**Examples:**
```bash
meta rollback component scraper-capabilities --to-version v2.0.0
meta rollback component scraper-capabilities --to-commit abc123def456
meta rollback lock manifests/components.lock.prod.yaml
meta rollback store component-name abc123def456...
meta rollback list
meta rollback snapshot --output backup.yaml
```

---

## Command: `meta health`

Check component health and system status.

**Options:**
- `--component, -c` - Check specific component
- `--all, -a` - Check all components
- `--env, -e` - Environment to check against
- `--build` - Check if component builds
- `--tests` - Check if component tests pass
- `--manifests, -m` - Manifests directory (default: "manifests")

**What it checks:**
- Component exists
- Version matches manifest/lock file
- Dependencies available
- Lock file sync (if using locked mode)
- Builds successfully (optional)
- Tests pass (optional)

**Examples:**
```bash
meta health --component scraper-capabilities
meta health --all --env staging
meta health --all --build --tests
meta health --component agent-core --env prod
```

---

## Command: `meta config`

Manage configuration (project and global).

**Subcommands:**
- `meta config get [key]` - Get config value(s)
- `meta config set <key> <value>` - Set config value
- `meta config init` - Initialize config file
- `meta config unset <key>` - Remove config value

**Options:**
- `--global, -g` - Use global config (`~/.meta/config.yaml`)

**Configuration options:**
- `default_env` - Default environment (default: "dev")
- `manifests_dir` - Manifests directory (default: "manifests")
- `parallel_jobs` - Number of parallel jobs (default: 4)
- `show_progress` - Show progress bars (default: true)
- `log_level` - Logging level (default: "INFO")
- `remote_cache` - Remote cache URL (optional)
- `remote_store` - Remote store URL (optional)

**Examples:**
```bash
meta config get default_env
meta config set default_env staging
meta config set parallel_jobs 8
meta config set remote_cache s3://bucket/cache
meta config init
meta config  # Show all config
```

**Note:** Configuration priority: Environment variables > Project config > Global config > Defaults

---

## Command: `meta version`

Shows meta-repo CLI version.

**No options**

**Examples:**
```bash
meta version
```

---

## Common Patterns

### All options work in any position (except `exec` which needs special handling)

```bash
# These are equivalent:
meta validate --env staging --skip-bazel
meta validate --skip-bazel --env staging

# These are equivalent:
meta plan --env dev --component agent-core
meta plan --component agent-core --env dev
```

### For `exec`, options can come before or after the command

```bash
# Natural pattern (options after)
meta exec pytest tests/ --component agent-core

# Alternative pattern (options before)
meta exec --component agent-core "pytest tests/"
```

