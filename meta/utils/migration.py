"""Component migration utilities."""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from meta.utils.logger import log, success, error
from meta.utils.discovery import discover_components, detect_component_type, validate_component_structure


def analyze_repo_structure(repo_path: str):
    """Analyze repository structure for migration."""
    path = Path(repo_path)
    
    if not path.exists():
        error(f"Path does not exist: {repo_path}")
        return {}
    
    analysis = {
        "path": str(path),
        "components": [],
        "suggestions": []
    }
    
    # Discover components
    components = discover_components(str(path), recursive=True)
    analysis["components"] = components
    
    # Analyze structure
    for comp in components:
        comp_path = Path(comp["path"])
        valid, errors = validate_component_structure(comp_path)
        
        suggestions = []
        if not valid:
            suggestions.append(f"Fix structure issues: {', '.join(errors)}")
        
        # Check for contracts
        if not (comp_path / "contracts").exists():
            suggestions.append("Add contracts directory")
        
        # Check for tests
        if not (comp_path / "tests").exists():
            suggestions.append("Add tests directory")
        
        comp["suggestions"] = suggestions
    
    return analysis


def generate_migration_plan(source_path: str, target_component: str,
                           target_dir: str = "components"):
    """Generate migration plan."""
    analysis = analyze_repo_structure(source_path)
    
    if not analysis:
        return {}
    
    plan = {
        "source": source_path,
        "target": f"{target_dir}/{target_component}",
        "components": [],
        "steps": []
    }
    
    for comp in analysis.get("components", []):
        comp_plan = {
            "name": comp["name"],
            "source": comp["path"],
            "target": f"{target_dir}/{comp['name']}",
            "type": comp["type"],
            "actions": []
        }
        
        # Copy files
        comp_plan["actions"].append(f"Copy {comp['path']} to {comp_plan['target']}")
        
        # Create contracts if missing
        if "Add contracts directory" in comp.get("suggestions", []):
            comp_plan["actions"].append("Create contracts directory")
        
        # Create tests if missing
        if "Add tests directory" in comp.get("suggestions", []):
            comp_plan["actions"].append("Create tests directory")
        
        # Fix structure issues
        if comp.get("suggestions"):
            comp_plan["actions"].extend(comp["suggestions"])
        
        plan["components"].append(comp_plan)
    
    return plan


def execute_migration(plan: Dict[str, Any], dry_run: bool = False) -> bool:
    """Execute migration plan."""
    if dry_run:
        log("DRY RUN - No changes will be made")
        for comp in plan.get("components", []):
            log(f"\nComponent: {comp['name']}")
            for action in comp.get("actions", []):
                log(f"  - {action}")
        return True
    
    for comp in plan.get("components", []):
        source = Path(comp["source"])
        target = Path(comp["target"])
        
        if target.exists():
            error(f"Target already exists: {target}")
            continue
        
        # Copy component
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target)
        success(f"Copied {comp['name']} to {target}")
        
        # Create missing directories
        if "Create contracts directory" in comp.get("actions", []):
            (target / "contracts").mkdir(exist_ok=True)
        
        if "Create tests directory" in comp.get("actions", []):
            (target / "tests").mkdir(exist_ok=True)
    
    return True

