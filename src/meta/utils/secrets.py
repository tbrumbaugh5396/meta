"""Secrets management utilities."""

import os
from typing import Optional, Dict, Any
from meta.utils.logger import log, error


class SecretsManager:
    """Base class for secrets management."""
    
    def get(self, key: str) -> Optional[str]:
        """Get a secret value."""
        raise NotImplementedError
    
    def set(self, key: str, value: str) -> bool:
        """Set a secret value."""
        raise NotImplementedError


class EnvironmentSecretsManager(SecretsManager):
    """Secrets manager using environment variables."""
    
    def get(self, key: str) -> Optional[str]:
        """Get secret from environment variable."""
        return os.getenv(key)
    
    def set(self, key: str, value: str) -> bool:
        """Set secret as environment variable (current process only)."""
        os.environ[key] = value
        return True


class VaultSecretsManager(SecretsManager):
    """Secrets manager using HashiCorp Vault."""
    
    def __init__(self, vault_addr: str, vault_token: Optional[str] = None):
        self.vault_addr = vault_addr
        self.vault_token = vault_token or os.getenv("VAULT_TOKEN")
        self._client = None
    
    def _get_client(self):
        """Get Vault client (lazy import)."""
        if self._client is None:
            try:
                import hvac
                self._client = hvac.Client(url=self.vault_addr, token=self.vault_token)
            except ImportError:
                error("hvac not installed. Install with: pip install hvac")
                return None
        return self._client
    
    def get(self, key: str, path: str = "secret") -> Optional[str]:
        """Get secret from Vault."""
        client = self._get_client()
        if not client:
            return None
        
        try:
            response = client.secrets.kv.v2.read_secret_version(path=path)
            return response.get("data", {}).get("data", {}).get(key)
        except Exception as e:
            error(f"Failed to get secret from Vault: {e}")
            return None
    
    def set(self, key: str, value: str, path: str = "secret") -> bool:
        """Set secret in Vault."""
        client = self._get_client()
        if not client:
            return False
        
        try:
            client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret={key: value}
            )
            return True
        except Exception as e:
            error(f"Failed to set secret in Vault: {e}")
            return False


class AWSSecretsManager(SecretsManager):
    """Secrets manager using AWS Secrets Manager."""
    
    def __init__(self, region: Optional[str] = None):
        self.region = region or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self._client = None
    
    def _get_client(self):
        """Get boto3 client (lazy import)."""
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client('secretsmanager', region_name=self.region)
            except ImportError:
                error("boto3 not installed. Install with: pip install boto3")
                return None
        return self._client
    
    def get(self, key: str) -> Optional[str]:
        """Get secret from AWS Secrets Manager."""
        client = self._get_client()
        if not client:
            return None
        
        try:
            response = client.get_secret_value(SecretId=key)
            import json
            secret = json.loads(response['SecretString'])
            return secret.get(key) if isinstance(secret, dict) else response['SecretString']
        except Exception as e:
            error(f"Failed to get secret from AWS: {e}")
            return None
    
    def set(self, key: str, value: str) -> bool:
        """Set secret in AWS Secrets Manager."""
        client = self._get_client()
        if not client:
            return False
        
        try:
            import json
            client.create_secret(
                Name=key,
                SecretString=json.dumps({key: value})
            )
            return True
        except Exception as e:
            error(f"Failed to set secret in AWS: {e}")
            return False


def get_secrets_manager(backend: str = "env", **kwargs) -> SecretsManager:
    """Get secrets manager instance."""
    if backend == "vault":
        return VaultSecretsManager(**kwargs)
    elif backend == "aws":
        return AWSSecretsManager(**kwargs)
    else:
        return EnvironmentSecretsManager()


