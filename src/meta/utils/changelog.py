"""Changelog management utilities."""

import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from meta.utils.logger import log, error, success
from meta.utils.git import get_current_version


def parse_commit_message(commit_msg: str) -> Dict[str, Any]:
    """Parse commit message for changelog entry."""
    # Common commit message patterns
    patterns = {
        "feature": r"^(feat|feature|add):\s*(.+)",
        "fix": r"^(fix|bugfix|bug):\s*(.+)",
        "breaking": r"^(breaking|break):\s*(.+)",
        "docs": r"^(doc|docs|documentation):\s*(.+)",
        "refactor": r"^(refactor|ref):\s*(.+)",
        "test": r"^(test|tests):\s*(.+)",
        "chore": r"^(chore|misc):\s*(.+)",
    }
    
    commit_msg = commit_msg.strip()
    change_type = "chore"
    description = commit_msg
    
    for change_type_key, pattern in patterns.items():
        match = re.match(pattern, commit_msg, re.IGNORECASE)
        if match:
            change_type = change_type_key
            description = match.group(2) if len(match.groups()) > 1 else match.group(0)
            break
    
    return {
        "type": change_type,
        "description": description,
        "raw": commit_msg
    }


def get_commits_since(component_path: str, since: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get commits since a version or date."""
    try:
        cmd = ["git", "-C", component_path, "log", "--pretty=format:%H|%s|%ai", "--reverse"]
        
        if since:
            # Check if it's a version tag
            if since.startswith("v") or since.replace(".", "").isdigit():
                cmd.append(f"{since}..HEAD")
            else:
                # Assume it's a date
                cmd.append(f"--since={since}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return []
        
        commits = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("|", 2)
            if len(parts) >= 2:
                commits.append({
                    "hash": parts[0][:8],
                    "message": parts[1],
                    "date": parts[2] if len(parts) > 2 else None
                })
        
        return commits
    except Exception as e:
        error(f"Failed to get commits: {e}")
        return []


def generate_changelog_entry(component: str, version: str,
                            component_path: str,
                            since: Optional[str] = None) -> str:
    """Generate changelog entry for a version."""
    commits = get_commits_since(component_path, since)
    
    if not commits:
        return f"## [{version}] - {datetime.utcnow().strftime('%Y-%m-%d')}\n\nNo changes.\n"
    
    # Categorize commits
    categories = {
        "feature": [],
        "fix": [],
        "breaking": [],
        "docs": [],
        "refactor": [],
        "test": [],
        "chore": []
    }
    
    for commit in commits:
        parsed = parse_commit_message(commit["message"])
        categories[parsed["type"]].append(parsed["description"])
    
    # Build changelog
    lines = [f"## [{version}] - {datetime.utcnow().strftime('%Y-%m-%d')}", ""]
    
    if categories["breaking"]:
        lines.append("### Breaking Changes")
        for desc in categories["breaking"]:
            lines.append(f"- {desc}")
        lines.append("")
    
    if categories["feature"]:
        lines.append("### Added")
        for desc in categories["feature"]:
            lines.append(f"- {desc}")
        lines.append("")
    
    if categories["fix"]:
        lines.append("### Fixed")
        for desc in categories["fix"]:
            lines.append(f"- {desc}")
        lines.append("")
    
    if categories["refactor"]:
        lines.append("### Changed")
        for desc in categories["refactor"]:
            lines.append(f"- {desc}")
        lines.append("")
    
    if categories["docs"]:
        lines.append("### Documentation")
        for desc in categories["docs"]:
            lines.append(f"- {desc}")
        lines.append("")
    
    if categories["test"]:
        lines.append("### Tests")
        for desc in categories["test"]:
            lines.append(f"- {desc}")
        lines.append("")
    
    if categories["chore"]:
        lines.append("### Miscellaneous")
        for desc in categories["chore"]:
            lines.append(f"- {desc}")
        lines.append("")
    
    return "\n".join(lines)


def update_changelog(component: str, version: str,
                   component_path: str,
                   changelog_path: Optional[str] = None,
                   since: Optional[str] = None) -> bool:
    """Update changelog file."""
    if changelog_path is None:
        changelog_path = str(Path(component_path) / "CHANGELOG.md")
    
    entry = generate_changelog_entry(component, version, component_path, since)
    
    changelog_file = Path(changelog_path)
    
    if changelog_file.exists():
        with open(changelog_file) as f:
            existing = f.read()
        
        # Insert new entry at the top (after title if exists)
        if existing.startswith("#"):
            # Find end of header
            header_end = existing.find("\n\n")
            if header_end > 0:
                header = existing[:header_end + 2]
                rest = existing[header_end + 2:]
                new_content = header + entry + "\n" + rest
            else:
                new_content = existing + "\n\n" + entry
        else:
            new_content = entry + "\n\n" + existing
    else:
        new_content = f"# Changelog\n\n{entry}\n"
    
    with open(changelog_file, 'w') as f:
        f.write(new_content)
    
    return True


