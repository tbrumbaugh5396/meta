# Phase 4 Enhancements: Health Checks, CI/CD, and Configuration

## Overview

Phase 4 adds three critical production-ready features:

1. **Health Checks** - Quick validation that components are working
2. **CI/CD Integration Examples** - Templates for all major CI/CD systems
3. **Configuration Management** - Per-project and global config files

## 1. Health Checks

### Purpose

Quick validation that components are working correctly before deployment or after incidents.

### Commands

#### Check Single Component

```bash
meta health --component scraper-capabilities
meta health --component scraper-capabilities --env prod
meta health --component scraper-capabilities --build --tests
```

#### Check All Components

```bash
meta health --all
meta health --all --env staging
meta health --all --build --tests
```

### What It Checks

- **Exists** - Component directory exists
- **Version** - Component version matches manifest/lock file
- **Dependencies** - All dependencies are available
- **Lock File Sync** - Component matches lock file (if using locked mode)
- **Builds** - Component builds successfully (optional, `--build`)
- **Tests** - Component tests pass (optional, `--tests`)

### Benefits

- **Quick Validation** - Verify system health in seconds
- **Pre-Deployment** - Catch issues before deploying
- **Post-Incident** - Verify recovery after incidents
- **CI/CD Integration** - Use in pipelines to verify deployments

## 2. CI/CD Integration Examples

### Purpose

Ready-to-use templates for all major CI/CD systems to accelerate adoption.

### Supported Systems

- **GitHub Actions** - `.github/workflows/meta-apply.yml`
- **GitLab CI** - `.gitlab-ci.yml`
- **Jenkins** - `Jenkinsfile`
- **CircleCI** - `.circleci/config.yml`
- **Azure DevOps** - `azure-pipelines.yml`

### Common Workflow

All examples follow this pattern:

1. **Validate** - Check system correctness
2. **Lock** - Generate lock file for reproducibility
3. **Apply** - Deploy components
4. **Test** - Run tests
5. **Health Check** - Verify everything is working

### Example: GitHub Actions

```yaml
name: Meta-Repo Apply

on:
  push:
    branches: [main, develop]

jobs:
  apply:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: |
          pip install -r requirements.txt
          pip install -e .
      - run: meta validate --env staging
      - run: |
          meta lock --env staging
          meta apply --env staging --locked --parallel
      - run: meta health --all --env staging
```

### Benefits

- **Faster Adoption** - Copy-paste ready templates
- **Best Practices** - Follows recommended workflows
- **Consistency** - Same pattern across all systems
- **Documentation** - See `CI_CD_GUIDE.md` for detailed guide

## 3. Configuration Management

### Purpose

Per-project and global configuration files to reduce repetitive flags and improve workflow.

### Configuration Files

- **Global Config** - `~/.meta/config.yaml` (user-wide defaults)
- **Project Config** - `.meta/config.yaml` (project-specific overrides)

### Commands

#### Get Config Value

```bash
meta config get default_env
meta config get remote_cache
meta config get  # Show all config
```

#### Set Config Value

```bash
meta config set default_env staging
meta config set parallel_jobs 8
meta config set remote_cache s3://bucket/cache
meta config set --global default_env dev  # Global config
```

#### Initialize Config

```bash
meta config init  # Project config
meta config init --global  # Global config
```

#### Remove Config Value

```bash
meta config unset remote_cache
meta config unset --global default_env
```

### Configuration Options

- `default_env` - Default environment (default: "dev")
- `manifests_dir` - Manifests directory (default: "manifests")
- `parallel_jobs` - Number of parallel jobs (default: 4)
- `show_progress` - Show progress bars (default: true)
- `log_level` - Logging level (default: "INFO")
- `remote_cache` - Remote cache URL (optional)
- `remote_store` - Remote store URL (optional)

### Environment Variables

You can also use environment variables (takes precedence):

```bash
export META_DEFAULT_ENV=staging
export META_MANIFESTS_DIR=manifests
export META_PARALLEL_JOBS=8
export META_SHOW_PROGRESS=false
export META_REMOTE_CACHE=s3://bucket/cache
```

### Priority Order

1. Environment variables (highest)
2. Project config (`.meta/config.yaml`)
3. Global config (`~/.meta/config.yaml`)
4. Defaults (lowest)

### Benefits

- **Less Repetition** - Set defaults once, use everywhere
- **Team Consistency** - Share project config via git
- **Personal Preferences** - Global config for your defaults
- **CI/CD Friendly** - Use environment variables in pipelines

## Integration

All three features work together:

```bash
# 1. Configure defaults
meta config set default_env staging
meta config set parallel_jobs 8

# 2. Apply (uses config defaults)
meta apply --all  # Uses staging and 8 jobs from config

# 3. Check health
meta health --all --env staging

# 4. In CI/CD, use health checks
meta health --all --env staging --build --tests
```

## Files Added

### Utilities
- `meta/utils/health.py` - Health check utilities
- `meta/utils/config.py` - Configuration management

### Commands
- `meta/commands/health.py` - Health check commands
- `meta/commands/config.py` - Configuration commands

### CI/CD Examples
- `.github/workflows/meta-apply.yml` - GitHub Actions
- `.gitlab-ci.yml` - GitLab CI
- `Jenkinsfile` - Jenkins
- `.circleci/config.yml` - CircleCI
- `azure-pipelines.yml` - Azure DevOps
- `CI_CD_GUIDE.md` - Complete CI/CD guide

### Tests
- `tests/unit/test_health.py`
- `tests/unit/test_config.py`

## Files Modified

- `meta/commands/apply.py` - Uses config for defaults
- `meta/cli.py` - Added health and config commands

## Benefits Summary

1. **Production Ready** - Health checks catch issues early
2. **Faster Adoption** - CI/CD templates ready to use
3. **Better UX** - Configuration reduces repetitive flags
4. **Team Collaboration** - Share config via git
5. **CI/CD Integration** - Health checks in pipelines

## Next Steps

Optional future enhancements:
- Health check history tracking
- More CI/CD system examples
- Configuration validation
- Health check scheduling
- Automated health monitoring


