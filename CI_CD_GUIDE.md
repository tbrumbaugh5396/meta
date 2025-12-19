# CI/CD Integration Guide

This guide shows how to integrate the meta-repo CLI into various CI/CD systems.

## Overview

The meta-repo CLI is designed to work seamlessly with CI/CD pipelines. Common workflow:

1. **Validate** - Check system correctness
2. **Lock** - Generate lock file for reproducibility
3. **Apply** - Deploy components
4. **Test** - Run tests
5. **Health Check** - Verify everything is working

## GitHub Actions

See `.github/workflows/meta-apply.yml` for a complete example.

### Basic Workflow

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
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .
      
      - name: Validate
        run: meta validate --env staging
      
      - name: Apply
        run: |
          meta lock --env staging
          meta apply --env staging --locked --parallel
      
      - name: Health check
        run: meta health --all --env staging
```

### With S3 Remote Cache

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v2
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1

- name: Apply with remote cache
  run: |
    meta cache build component --source build/ --remote s3://bucket/cache
    meta apply --env staging --locked
```

## GitLab CI

See `.gitlab-ci.yml` for a complete example.

### Basic Pipeline

```yaml
stages:
  - validate
  - apply
  - test

variables:
  META_ENV: ${CI_COMMIT_REF_NAME == "main" ? "prod" : "staging"}

validate:
  stage: validate
  image: python:3.9
  script:
    - pip install -r requirements.txt
    - pip install -e .
    - meta validate --env $META_ENV

apply:
  stage: apply
  image: python:3.9
  script:
    - pip install -r requirements.txt
    - pip install -e .
    - meta lock --env $META_ENV
    - meta apply --env $META_ENV --locked --parallel
```

## Jenkins

See `Jenkinsfile` for a complete example.

### Basic Pipeline

```groovy
pipeline {
    agent any
    
    environment {
        META_ENV = "${env.BRANCH_NAME == 'main' ? 'prod' : 'staging'}"
    }
    
    stages {
        stage('Validate') {
            steps {
                sh 'meta validate --env ${META_ENV}'
            }
        }
        
        stage('Apply') {
            steps {
                sh '''
                    meta lock --env ${META_ENV}
                    meta apply --env ${META_ENV} --locked --parallel
                '''
            }
        }
    }
}
```

## CircleCI

See `.circleci/config.yml` for a complete example.

### Basic Config

```yaml
version: 2.1

jobs:
  apply:
    docker:
      - image: cimg/python:3.9
    steps:
      - checkout
      - run:
          name: Install
          command: |
            pip install -r requirements.txt
            pip install -e .
      - run:
          name: Apply
          command: |
            META_ENV=${CIRCLE_BRANCH == "main" ? "prod" : "staging"}
            meta lock --env $META_ENV
            meta apply --env $META_ENV --locked --parallel
```

## Azure DevOps

See `azure-pipelines.yml` for a complete example.

### Basic Pipeline

```yaml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  META_ENV: $[coalesce(variables['META_ENV'], variables['Build.SourceBranchName'] == 'main' ? 'prod' : 'staging')]

stages:
  - stage: Apply
    jobs:
      - job: Apply
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.9'
          - script: |
              pip install -r requirements.txt
              pip install -e .
          - script: |
              meta lock --env $(META_ENV)
              meta apply --env $(META_ENV) --locked --parallel
```

## Best Practices

### 1. Always Use Lock Files in CI/CD

```bash
meta lock --env staging
meta apply --env staging --locked
```

This ensures reproducible builds.

### 2. Use Parallel Execution

```bash
meta apply --env staging --parallel --jobs 4
```

Faster deployments for large systems.

### 3. Run Health Checks

```bash
meta health --all --env staging --build --tests
```

Verify everything is working after deployment.

### 4. Use Remote Cache

Configure remote cache for faster builds:

```bash
# In CI/CD
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
meta cache build component --source build/ --remote s3://bucket/cache
```

### 5. Environment-Specific Configs

Use different environments for different branches:

```bash
# In CI/CD script
META_ENV=${BRANCH == "main" ? "prod" : "staging"}
meta apply --env $META_ENV --locked
```

### 6. Fail Fast

Run validation before applying:

```bash
meta validate --env staging || exit 1
meta apply --env staging --locked
```

### 7. Artifact Lock Files

Save lock files as artifacts:

```yaml
# GitHub Actions
- uses: actions/upload-artifact@v3
  with:
    name: lock-files
    path: manifests/components.lock.*.yaml
```

## Environment Variables

You can configure the CLI using environment variables:

```bash
export META_DEFAULT_ENV=staging
export META_MANIFESTS_DIR=manifests
export META_PARALLEL_JOBS=4
export META_SHOW_PROGRESS=false
export META_REMOTE_CACHE=s3://bucket/cache
export META_REMOTE_STORE=gs://bucket/store
```

## Troubleshooting

### Build Failures

1. Check health: `meta health --all --env staging`
2. Check logs: `meta apply --env staging --verbose`
3. Validate first: `meta validate --env staging`

### Cache Issues

1. Clear cache: `meta cache invalidate --all`
2. Check remote: `meta cache list`
3. Verify credentials for remote cache

### Lock File Issues

1. Regenerate: `meta lock --env staging`
2. Validate: `meta lock validate --env staging`
3. Compare: `meta lock compare dev staging`

## Examples

See the example files in the repository:
- `.github/workflows/meta-apply.yml` - GitHub Actions
- `.gitlab-ci.yml` - GitLab CI
- `Jenkinsfile` - Jenkins
- `.circleci/config.yml` - CircleCI
- `azure-pipelines.yml` - Azure DevOps


