"""Changeset utilities for atomic cross-repo operations."""

import yaml
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from meta.utils.logger import log, error, success
from meta.utils.manifest import find_meta_repo_root, get_components
from meta.utils.git import get_commit_sha, get_current_version


CHANGESET_DIR = Path(".meta/changesets")
CHANGESET_INDEX = CHANGESET_DIR / "index.yaml"


class Changeset:
    """Represents a changeset (atomic transaction across repos)."""
    
    def __init__(
        self,
        changeset_id: str,
        description: str,
        author: Optional[str] = None,
        timestamp: Optional[str] = None,
        status: str = "in-progress",
        repos: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = changeset_id
        self.description = description
        self.author = author or "unknown"
        self.timestamp = timestamp or datetime.now().isoformat()
        self.status = status  # in-progress, committed, failed, rolled-back
        self.repos = repos or []
        self.metadata = metadata or {}
    
    def add_repo_commit(
        self,
        repo_name: str,
        repo_url: str,
        commit_sha: str,
        branch: str,
        message: str
    ):
        """Add a commit to this changeset."""
        self.repos.append({
            "name": repo_name,
            "repo": repo_url,
            "commit": commit_sha,
            "branch": branch,
            "message": message
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "author": self.author,
            "description": self.description,
            "status": self.status,
            "repos": self.repos,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Changeset":
        """Create from dictionary."""
        return cls(
            changeset_id=data["id"],
            description=data["description"],
            author=data.get("author"),
            timestamp=data.get("timestamp"),
            status=data.get("status", "in-progress"),
            repos=data.get("repos", []),
            metadata=data.get("metadata", {})
        )


def ensure_changeset_dir():
    """Ensure changeset directory exists."""
    CHANGESET_DIR.mkdir(parents=True, exist_ok=True)
    if not CHANGESET_INDEX.exists():
        with open(CHANGESET_INDEX, 'w') as f:
            yaml.dump({"changesets": []}, f)


def generate_changeset_id() -> str:
    """Generate a unique changeset ID."""
    # Use short UUID for readability
    return str(uuid.uuid4())[:8]


def create_changeset(description: str, author: Optional[str] = None) -> Changeset:
    """Create a new changeset."""
    ensure_changeset_dir()
    
    changeset_id = generate_changeset_id()
    changeset = Changeset(
        changeset_id=changeset_id,
        description=description,
        author=author
    )
    
    # Save changeset
    save_changeset(changeset)
    
    # Add to index
    add_to_index(changeset_id)
    
    return changeset


def save_changeset(changeset: Changeset):
    """Save a changeset to disk."""
    ensure_changeset_dir()
    
    changeset_file = CHANGESET_DIR / f"{changeset.id}.yaml"
    with open(changeset_file, 'w') as f:
        yaml.dump(changeset.to_dict(), f, default_flow_style=False)


def load_changeset(changeset_id: str) -> Optional[Changeset]:
    """Load a changeset by ID."""
    changeset_file = CHANGESET_DIR / f"{changeset_id}.yaml"
    
    if not changeset_file.exists():
        return None
    
    try:
        with open(changeset_file) as f:
            data = yaml.safe_load(f)
            return Changeset.from_dict(data)
    except Exception as e:
        error(f"Failed to load changeset {changeset_id}: {e}")
        return None


def add_to_index(changeset_id: str):
    """Add changeset ID to index."""
    ensure_changeset_dir()
    
    if CHANGESET_INDEX.exists():
        with open(CHANGESET_INDEX) as f:
            index = yaml.safe_load(f) or {}
    else:
        index = {}
    
    if "changesets" not in index:
        index["changesets"] = []
    
    if changeset_id not in index["changesets"]:
        index["changesets"].append(changeset_id)
    
    with open(CHANGESET_INDEX, 'w') as f:
        yaml.dump(index, f, default_flow_style=False)


def list_changesets(limit: Optional[int] = None, status_filter: Optional[str] = None) -> List[Changeset]:
    """List all changesets."""
    ensure_changeset_dir()
    
    if not CHANGESET_INDEX.exists():
        return []
    
    try:
        with open(CHANGESET_INDEX) as f:
            index = yaml.safe_load(f) or {}
    except:
        return []
    
    changeset_ids = index.get("changesets", [])
    if limit:
        changeset_ids = changeset_ids[-limit:]
    
    changesets = []
    for changeset_id in reversed(changeset_ids):  # Most recent first
        changeset = load_changeset(changeset_id)
        if changeset:
            if status_filter is None or changeset.status == status_filter:
                changesets.append(changeset)
    
    return changesets


def find_changeset_by_commit(repo_name: str, commit_sha: str) -> Optional[Changeset]:
    """Find changeset containing a specific commit."""
    changesets = list_changesets()
    
    for changeset in changesets:
        for repo in changeset.repos:
            if repo["name"] == repo_name and repo["commit"] == commit_sha:
                return changeset
    
    return None


def extract_changeset_id_from_message(message: str) -> Optional[str]:
    """Extract changeset ID from commit message."""
    # Look for [changeset:abc123] pattern
    import re
    match = re.search(r'\[changeset:([a-f0-9-]+)\]', message, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def get_current_changeset() -> Optional[Changeset]:
    """Get the most recent in-progress changeset."""
    changesets = list_changesets(status_filter="in-progress")
    if changesets:
        return changesets[0]  # Most recent
    return None

