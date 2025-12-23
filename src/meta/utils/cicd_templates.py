"""CI/CD template utilities."""

from pathlib import Path
from typing import Dict, Any, Optional
from meta.utils.logger import log, success, error


GITHUB_ACTIONS_TEMPLATE = """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          echo "Add your test commands here"
"""

GITLAB_CI_TEMPLATE = """stages:
  - test
  - build
  - deploy

test:
  stage: test
  script:
    - echo "Add your test commands here"
"""

JENKINS_TEMPLATE = """pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                echo 'Add your test commands here'
            }
        }
    }
}
"""


def generate_cicd_template(component: str,
                           provider: str,
                           component_path: Path) -> str:
    """Generate CI/CD template for a component."""
    templates = {
        "github": GITHUB_ACTIONS_TEMPLATE,
        "gitlab": GITLAB_CI_TEMPLATE,
        "jenkins": JENKINS_TEMPLATE,
    }
    
    template = templates.get(provider.lower())
    if not template:
        error(f"Unsupported CI/CD provider: {provider}")
        return ""
    
    return template


def scaffold_cicd(component: str,
                 provider: str,
                 component_path: Path) -> bool:
    """Scaffold CI/CD configuration for a component."""
    template = generate_cicd_template(component, provider, component_path)
    
    if not template:
        return False
    
    # Determine output file
    output_files = {
        "github": ".github/workflows/ci.yml",
        "gitlab": ".gitlab-ci.yml",
        "jenkins": "Jenkinsfile",
    }
    
    output_file = component_path / output_files.get(provider.lower(), "ci.yml")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    output_file.write_text(template)
    success(f"Created CI/CD configuration: {output_file}")
    
    return True


def validate_cicd(component: str,
                 component_path: Path) -> bool:
    """Validate CI/CD configuration."""
    # Check for common CI/CD files
    cicd_files = [
        ".github/workflows/ci.yml",
        ".gitlab-ci.yml",
        "Jenkinsfile",
        ".circleci/config.yml",
        ".travis.yml",
    ]
    
    found = False
    for cicd_file in cicd_files:
        if (component_path / cicd_file).exists():
            found = True
            log(f"Found CI/CD config: {cicd_file}")
    
    if not found:
        warning(f"No CI/CD configuration found for {component}")
    
    return found


