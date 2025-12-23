# Configuration Management

## Overview

The meta-repo CLI provides per-project and global configuration files to reduce repetitive flags and improve workflow consistency across team members.

## Configuration Files

### Global Config

User-wide defaults stored in `~/.meta/config.yaml`:

```yaml
default_env: dev
manifests_dir: manifests
parallel_jobs: 4
show_progress: true
log_level: INFO
remote_cache: s3://my-bucket/cache
remote_store: s3://my-bucket/store
```

### Project Config

Project-specific overrides stored in `.meta/config.yaml`:

```yaml
default_env: staging
parallel_jobs: 8
remote_cache: s3://project-bucket/cache
```

## Commands

### Get Config Value

```bash
meta config get default_env
meta config get remote_cache
meta config get  # Show all config
```

### Set Config Value

```bash
meta config set default_env staging
meta config set parallel_jobs 8
meta config set remote_cache s3://bucket/cache
meta config set --global default_env dev  # Global config
```

### Initialize Config

```bash
meta config init  # Project config
meta config init --global  # Global config
```

### Remove Config Value

```bash
meta config unset remote_cache
meta config unset --global default_env
```

## Configuration Options

### Core Options

- `default_env` - Default environment (default: "dev")
- `manifests_dir` - Manifests directory (default: "manifests")
- `parallel_jobs` - Number of parallel jobs (default: 4)
- `show_progress` - Show progress bars (default: true)
- `log_level` - Logging level (default: "INFO")

### Remote Options

- `remote_cache` - Remote cache URL (optional)
- `remote_store` - Remote store URL (optional)

## Environment Variables

You can also use environment variables (takes precedence over config files):

```bash
export META_DEFAULT_ENV=staging
export META_MANIFESTS_DIR=manifests
export META_PARALLEL_JOBS=8
export META_SHOW_PROGRESS=false
export META_REMOTE_CACHE=s3://bucket/cache
export META_REMOTE_STORE=s3://bucket/store
```

## Priority Order

Configuration is resolved in this order (highest to lowest):

1. **Environment variables** (highest priority)
2. **Project config** (`.meta/config.yaml`)
3. **Global config** (`~/.meta/config.yaml`)
4. **Defaults** (lowest priority)

## Usage Examples

### Setting Defaults

```bash
# Set project default environment
meta config set default_env staging

# Set global parallel jobs
meta config set --global parallel_jobs 8

# Set remote cache for project
meta config set remote_cache s3://project-bucket/cache
```

### Using Configuration

Once configured, commands use the defaults automatically:

```bash
# Uses default_env from config
meta apply --all

# Uses parallel_jobs from config
meta apply --all --parallel

# Uses remote_cache from config
meta cache build component --source path/
```

### Overriding Configuration

You can still override config values with command-line flags:

```bash
# Override default_env for this command
meta apply --all --env prod

# Override parallel_jobs for this command
meta apply --all --parallel --jobs 16
```

## Team Collaboration

### Sharing Project Config

Project config (`.meta/config.yaml`) should be committed to git:

```bash
git add .meta/config.yaml
git commit -m "Add project configuration"
```

This ensures all team members use the same project defaults.

### Personal Preferences

Global config (`~/.meta/config.yaml`) is not committed to git, allowing each developer to set personal preferences:

```bash
# Personal preference for parallel jobs
meta config set --global parallel_jobs 16

# Personal preference for log level
meta config set --global log_level DEBUG
```

## CI/CD Integration

In CI/CD pipelines, use environment variables:

```yaml
# GitHub Actions example
env:
  META_DEFAULT_ENV: staging
  META_PARALLEL_JOBS: 8
  META_REMOTE_CACHE: s3://ci-bucket/cache

steps:
  - run: meta apply --all
```

## Benefits

1. **Less Repetition** - Set defaults once, use everywhere
2. **Team Consistency** - Share project config via git
3. **Personal Preferences** - Global config for your defaults
4. **CI/CD Friendly** - Use environment variables in pipelines
5. **Flexibility** - Override with command-line flags when needed

## Implementation Details

### Files

- `meta/utils/config.py` - Configuration management
- `meta/commands/config.py` - Configuration commands

### Configuration Resolution

1. Load defaults
2. Load global config (if exists)
3. Load project config (if exists)
4. Override with environment variables
5. Override with command-line flags

## Best Practices

1. **Commit Project Config** - Share project defaults via git
2. **Use Environment Variables in CI/CD** - More flexible than config files
3. **Set Sensible Defaults** - Make common workflows easy
4. **Document Custom Config** - Explain why certain values are set
5. **Review Config Changes** - Ensure team is aware of changes

