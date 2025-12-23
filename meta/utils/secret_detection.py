"""Secret detection utilities for scanning files during vendor operations."""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
from meta.utils.logger import log, warning, error


# Common secret patterns
SECRET_PATTERNS = [
    # API Keys
    (r'api[_-]?key["\s:=]+([a-zA-Z0-9_\-]{20,})', 'api_key'),
    (r'apikey["\s:=]+([a-zA-Z0-9_\-]{20,})', 'api_key'),
    (r'api[_-]?secret["\s:=]+([a-zA-Z0-9_\-]{20,})', 'api_secret'),
    
    # AWS
    (r'AKIA[0-9A-Z]{16}', 'aws_access_key'),
    (r'aws[_-]?secret[_-]?access[_-]?key["\s:=]+([a-zA-Z0-9+/]{40})', 'aws_secret_key'),
    
    # Passwords
    (r'password["\s:=]+([^\s"\']{8,})', 'password'),
    (r'passwd["\s:=]+([^\s"\']{8,})', 'password'),
    (r'pwd["\s:=]+([^\s"\']{8,})', 'password'),
    
    # Tokens
    (r'token["\s:=]+([a-zA-Z0-9_\-]{20,})', 'token'),
    (r'bearer["\s:=]+([a-zA-Z0-9_\-]{20,})', 'bearer_token'),
    (r'access[_-]?token["\s:=]+([a-zA-Z0-9_\-]{20,})', 'access_token'),
    
    # Private keys
    (r'-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----', 'private_key'),
    
    # Database credentials
    (r'database[_-]?password["\s:=]+([^\s"\']{8,})', 'db_password'),
    (r'db[_-]?pass["\s:=]+([^\s"\']{8,})', 'db_password'),
    
    # OAuth
    (r'oauth[_-]?token["\s:=]+([a-zA-Z0-9_\-]{20,})', 'oauth_token'),
    (r'client[_-]?secret["\s:=]+([a-zA-Z0-9_\-]{20,})', 'oauth_client_secret'),
    
    # Generic secrets
    (r'secret["\s:=]+([a-zA-Z0-9_\-+/=]{20,})', 'secret'),
    (r'secret[_-]?key["\s:=]+([a-zA-Z0-9_\-+/=]{20,})', 'secret_key'),
]


# Files/directories to exclude from scanning
EXCLUDE_PATTERNS = [
    '.git',
    'node_modules',
    '__pycache__',
    '.venv',
    'venv',
    'vendor',
    'dist',
    'build',
    '.vendor-info.yaml',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '*.so',
    '*.dylib',
    '*.dll',
]


def should_exclude_file(file_path: Path, exclude_patterns: Optional[List[str]] = None) -> bool:
    """Check if a file should be excluded from secret scanning."""
    if exclude_patterns is None:
        exclude_patterns = EXCLUDE_PATTERNS
    
    file_str = str(file_path)
    file_name = file_path.name
    
    for pattern in exclude_patterns:
        # Simple glob-like matching
        if pattern.startswith('*.'):
            if file_name.endswith(pattern[1:]):
                return True
        elif pattern in file_str:
            return True
    
    return False


def scan_file_for_secrets(file_path: Path, patterns: Optional[List[tuple]] = None) -> List[Dict[str, Any]]:
    """Scan a single file for secrets.
    
    Args:
        file_path: Path to file to scan
        patterns: List of (pattern, secret_type) tuples. Defaults to SECRET_PATTERNS.
    
    Returns:
        List of detected secrets with line numbers and types
    """
    if patterns is None:
        patterns = SECRET_PATTERNS
    
    if should_exclude_file(file_path):
        return []
    
    if not file_path.is_file():
        return []
    
    # Skip binary files
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        return []  # Skip files that can't be read
    
    # Limit file size (skip very large files)
    if len(content) > 1_000_000:  # 1MB
        return []
    
    detected = []
    
    for line_num, line in enumerate(content.split('\n'), 1):
        for pattern, secret_type in patterns:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                # Extract the secret value (first capture group or full match)
                secret_value = match.group(1) if match.groups() else match.group(0)
                # Truncate for display
                display_value = secret_value[:20] + '...' if len(secret_value) > 20 else secret_value
                
                detected.append({
                    'file': str(file_path),
                    'line': line_num,
                    'type': secret_type,
                    'value_preview': display_value,
                    'line_preview': line.strip()[:100]
                })
    
    return detected


def scan_directory_for_secrets(
    directory: Path,
    exclude_patterns: Optional[List[str]] = None,
    max_files: int = 10000
) -> Dict[str, Any]:
    """Scan a directory for secrets.
    
    Args:
        directory: Directory to scan
        exclude_patterns: Additional patterns to exclude
        max_files: Maximum number of files to scan (safety limit)
    
    Returns:
        Dictionary with scan results
    """
    if not directory.exists() or not directory.is_dir():
        return {
            'secrets_found': [],
            'total_files_scanned': 0,
            'total_secrets': 0,
            'error': f"Directory does not exist: {directory}"
        }
    
    secrets_found = []
    files_scanned = 0
    
    try:
        for file_path in directory.rglob('*'):
            if files_scanned >= max_files:
                warning(f"Reached max file limit ({max_files}), stopping scan")
                break
            
            if should_exclude_file(file_path, exclude_patterns):
                continue
            
            if file_path.is_file():
                file_secrets = scan_file_for_secrets(file_path)
                if file_secrets:
                    secrets_found.extend(file_secrets)
                files_scanned += 1
    except Exception as e:
        error(f"Error scanning directory: {e}")
        return {
            'secrets_found': secrets_found,
            'total_files_scanned': files_scanned,
            'total_secrets': len(secrets_found),
            'error': str(e)
        }
    
    return {
        'secrets_found': secrets_found,
        'total_files_scanned': files_scanned,
        'total_secrets': len(secrets_found),
        'error': None
    }


def detect_secrets_in_component(
    component_dir: Path,
    fail_on_secrets: bool = False
) -> Tuple[bool, Dict[str, Any]]:
    """Detect secrets in a component directory.
    
    Args:
        component_dir: Path to component directory
        fail_on_secrets: If True, return False when secrets are found
    
    Returns:
        Tuple of (is_safe, scan_results)
    """
    if not component_dir.exists():
        return True, {
            'secrets_found': [],
            'total_files_scanned': 0,
            'total_secrets': 0,
            'error': f"Component directory does not exist: {component_dir}"
        }
    
    results = scan_directory_for_secrets(component_dir)
    
    is_safe = results['total_secrets'] == 0
    
    if not is_safe and fail_on_secrets:
        error(f"Secrets detected in {component_dir}:")
        for secret in results['secrets_found'][:10]:  # Show first 10
            error(f"  {secret['type']} in {secret['file']}:{secret['line']}")
        if results['total_secrets'] > 10:
            error(f"  ... and {results['total_secrets'] - 10} more")
    
    return is_safe, results

