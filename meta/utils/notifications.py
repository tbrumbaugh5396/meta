"""Component notification utilities."""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from meta.utils.logger import log, success, error
# Note: config utilities are optional


NOTIFICATIONS_CONFIG = Path(".meta/notifications.yaml")


class NotificationManager:
    """Manages component notifications."""
    
    def __init__(self):
        self.config_file = NOTIFICATIONS_CONFIG
        self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load notification configuration."""
        if not self.config_file.exists():
            return {}
        
        try:
            import yaml
            with open(self.config_file) as f:
                return yaml.safe_load(f) or {}
        except:
            return {}
    
    def _save_config(self, config: Dict[str, Any]):
        """Save notification configuration."""
        import yaml
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    def setup(self, email: Optional[str] = None, slack_webhook: Optional[str] = None) -> bool:
        """Setup notification channels."""
        config = self._load_config()
        
        if email:
            config["email"] = email
        if slack_webhook:
            config["slack_webhook"] = slack_webhook
        
        self._save_config(config)
        return True
    
    def subscribe(self, component: str, events: List[str]) -> bool:
        """Subscribe to component events."""
        config = self._load_config()
        
        if "subscriptions" not in config:
            config["subscriptions"] = {}
        
        config["subscriptions"][component] = events
        self._save_config(config)
        return True
    
    def send_notification(self, event: str, component: str, message: str) -> bool:
        """Send a notification."""
        config = self._load_config()
        
        # Check if subscribed
        subscriptions = config.get("subscriptions", {})
        component_events = subscriptions.get(component, [])
        
        if event not in component_events and "*" not in component_events:
            return False  # Not subscribed to this event
        
        # Send email
        if "email" in config:
            self._send_email(config["email"], event, component, message)
        
        # Send Slack
        if "slack_webhook" in config:
            self._send_slack(config["slack_webhook"], event, component, message)
        
        return True
    
    def _send_email(self, email: str, event: str, component: str, message: str):
        """Send email notification."""
        # In a real implementation, use smtplib or sendmail
        log(f"Would send email to {email}: [{event}] {component}: {message}")
    
    def _send_slack(self, webhook: str, event: str, component: str, message: str):
        """Send Slack notification."""
        try:
            import requests
            payload = {
                "text": f"[{event}] {component}: {message}",
                "username": "Meta-Repo CLI"
            }
            requests.post(webhook, json=payload, timeout=5)
        except Exception as e:
            error(f"Failed to send Slack notification: {e}")


def get_notification_manager() -> NotificationManager:
    """Get notification manager instance."""
    return NotificationManager()

