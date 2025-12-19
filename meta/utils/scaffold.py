"""Component scaffolding utilities."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from meta.utils.logger import log, success, error
from meta.utils.manifest import get_components


COMPONENT_TEMPLATES = {
    "bazel": {
        "BUILD.bazel": """load("@rules_python//python:defs.bzl", "py_library", "py_test")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "{component_name}",
    srcs = glob(["src/**/*.py"]),
    deps = [
        # Add dependencies here
    ],
)

py_test(
    name = "{component_name}_test",
    srcs = glob(["tests/**/*.py"]),
    deps = [
        ":{component_name}",
    ],
)
""",
        "README.md": """# {component_name}

## Description

{description}

## Usage

```python
# Example usage
```

## Dependencies

- Add dependencies here

## Building

```bash
bazel build //...
bazel test //...
```
""",
        "src/__init__.py": """\"\"\"{component_name} package.\"\"\"
""",
        "tests/__init__.py": """\"\"\"Tests for {component_name}.\"\"\"
""",
    },
    "python": {
        "setup.py": """from setuptools import setup, find_packages

setup(
    name="{component_name}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Add dependencies here
    ],
    python_requires=">=3.8",
)
""",
        "README.md": """# {component_name}

## Description

{description}

## Installation

```bash
pip install -e .
```

## Usage

```python
# Example usage
```

## Dependencies

- Add dependencies here
""",
        "src/__init__.py": """\"\"\"{component_name} package.\"\"\"
""",
        "tests/__init__.py": """\"\"\"Tests for {component_name}.\"\"\"
""",
    },
    "npm": {
        "package.json": """{{
  "name": "{component_name}",
  "version": "0.1.0",
  "description": "{description}",
  "main": "src/index.js",
  "scripts": {{
    "test": "jest",
    "build": "tsc",
    "lint": "eslint src"
  }},
  "dependencies": {{
    // Add dependencies here
  }},
  "devDependencies": {{
    // Add dev dependencies here
  }}
}}
""",
        "README.md": """# {component_name}

## Description

{description}

## Installation

```bash
npm install
```

## Usage

```javascript
// Example usage
```

## Building

```bash
npm run build
npm test
```
""",
        "src/index.js": """// {component_name}
""",
    },
}


def create_component_structure(component_name: str, component_type: str,
                               description: Optional[str] = None,
                               component_dir: str = "components") -> bool:
    """Create component directory structure."""
    if component_type not in COMPONENT_TEMPLATES:
        error(f"Unsupported component type: {component_type}")
        error(f"Supported types: {', '.join(COMPONENT_TEMPLATES.keys())}")
        return False
    
    comp_path = Path(component_dir) / component_name
    if comp_path.exists():
        error(f"Component directory already exists: {comp_path}")
        return False
    
    if description is None:
        description = f"{component_name} component"
    
    # Create directory structure
    comp_path.mkdir(parents=True, exist_ok=True)
    
    # Get template
    template = COMPONENT_TEMPLATES[component_type]
    
    # Create files
    for file_path, content in template.items():
        file_full_path = comp_path / file_path
        file_full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Format content with component name and description
        formatted_content = content.format(
            component_name=component_name,
            description=description
        )
        
        with open(file_full_path, 'w') as f:
            f.write(formatted_content)
    
    # Create contracts directory
    contracts_dir = comp_path / "contracts"
    contracts_dir.mkdir(exist_ok=True)
    
    # Create example contract
    contract_file = contracts_dir / f"{component_name}_contract.py"
    contract_content = f'''"""Contract definition for {component_name}."""

from typing import Protocol


class {component_name.title().replace("-", "").replace("_", "")}Contract(Protocol):
    """Interface contract for {component_name}."""
    
    def method(self) -> None:
        """Example method."""
        ...
'''
    with open(contract_file, 'w') as f:
        f.write(contract_content)
    
    success(f"Created component structure: {comp_path}")
    log(f"Component type: {component_type}")
    log(f"Next steps:")
    log(f"  1. Review generated files in {comp_path}")
    log(f"  2. Add component to manifests/components.yaml")
    log(f"  3. Implement component functionality")
    
    return True


def generate_manifest_entry(component_name: str, component_type: str,
                           repo_url: Optional[str] = None,
                           version: str = "0.1.0") -> Dict[str, Any]:
    """Generate manifest entry for component."""
    entry = {
        "repo": repo_url or f"git@github.com:org/{component_name}.git",
        "version": version,
        "type": component_type,
    }
    
    if component_type == "bazel":
        entry["build_target"] = f"//..."
    
    return entry


