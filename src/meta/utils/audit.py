"""Audit logging utilities."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from meta.utils.logger import log, error


AUDIT_LOG_FILE = ".meta/audit.log"


class AuditLogger:
    """Audit logger for tracking operations."""
    
    def __init__(self, log_file: str = AUDIT_LOG_FILE):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, action: str, user: Optional[str] = None,
           component: Optional[str] = None,
           details: Optional[Dict[str, Any]] = None,
           success: bool = True):
        """Log an audit event."""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": action,
            "user": user or self._get_user(),
            "component": component,
            "success": success,
            "details": details or {}
        }
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            error(f"Failed to write audit log: {e}")
    
    def _get_user(self) -> str:
        """Get current user."""
        import os
        import getpass
        return os.getenv("USER") or os.getenv("USERNAME") or getpass.getuser()
    
    def query(self, action: Optional[str] = None,
             user: Optional[str] = None,
             component: Optional[str] = None,
             since: Optional[datetime] = None,
             days: Optional[int] = None) -> List[Dict[str, Any]]:
        """Query audit log."""
        if not self.log_file.exists():
            return []
        
        results = []
        cutoff = None
        
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
        elif since:
            cutoff = since
        
        try:
            with open(self.log_file) as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    try:
                        entry = json.loads(line)
                        
                        # Filter by criteria
                        if action and entry.get("action") != action:
                            continue
                        if user and entry.get("user") != user:
                            continue
                        if component and entry.get("component") != component:
                            continue
                        if cutoff:
                            entry_time = datetime.fromisoformat(entry.get("timestamp", "").replace("Z", "+00:00"))
                            if entry_time < cutoff:
                                continue
                        
                        results.append(entry)
                    except:
                        continue
        except Exception as e:
            error(f"Failed to read audit log: {e}")
        
        return results


def get_audit_logger() -> AuditLogger:
    """Get audit logger instance."""
    return AuditLogger()


