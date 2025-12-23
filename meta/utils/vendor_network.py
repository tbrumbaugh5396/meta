"""Network resilience utilities for vendor operations."""

import time
import subprocess
from typing import Callable, Any, Optional, Tuple
from meta.utils.logger import log, error, warning


def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    retry_on_exceptions: Tuple = (Exception,),
    *args,
    **kwargs
) -> Tuple[bool, Any]:
    """Execute a function with exponential backoff retry logic.
    
    Args:
        func: Function to execute
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Factor to multiply delay by on each retry
        retry_on_exceptions: Tuple of exceptions to retry on
        *args: Arguments to pass to function
        **kwargs: Keyword arguments to pass to function
    
    Returns:
        Tuple of (success, result)
    """
    delay = initial_delay
    
    for attempt in range(max_retries + 1):
        try:
            result = func(*args, **kwargs)
            if attempt > 0:
                log(f"Operation succeeded on attempt {attempt + 1}")
            return True, result
        
        except retry_on_exceptions as e:
            if attempt < max_retries:
                log(f"Attempt {attempt + 1} failed: {e}")
                log(f"Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
                delay = min(delay * backoff_factor, max_delay)
            else:
                error(f"Operation failed after {max_retries + 1} attempts: {e}")
                return False, e
        
        except Exception as e:
            # Don't retry on unexpected exceptions
            error(f"Unexpected error: {e}")
            return False, e
    
    return False, None


def git_clone_with_retry(
    repo_url: str,
    target_dir: str,
    max_retries: int = 3
) -> bool:
    """Clone a git repository with retry logic.
    
    Args:
        repo_url: Repository URL
        target_dir: Target directory
        max_retries: Maximum retry attempts
    
    Returns:
        True if successful
    """
    def clone_operation():
        result = subprocess.run(
            ["git", "clone", repo_url, target_dir],
            check=True,
            capture_output=True,
            text=True
        )
        return result
    
    success, result = retry_with_backoff(
        clone_operation,
        max_retries=max_retries,
        retry_on_exceptions=(subprocess.CalledProcessError, ConnectionError, TimeoutError)
    )
    
    return success


def git_checkout_with_retry(
    repo_dir: str,
    version: str,
    max_retries: int = 3
) -> bool:
    """Checkout a git version with retry logic.
    
    Args:
        repo_dir: Repository directory
        version: Version/tag to checkout
        max_retries: Maximum retry attempts
    
    Returns:
        True if successful
    """
    def checkout_operation():
        result = subprocess.run(
            ["git", "-C", repo_dir, "checkout", version],
            check=True,
            capture_output=True,
            text=True
        )
        return result
    
    success, result = retry_with_backoff(
        checkout_operation,
        max_retries=max_retries,
        retry_on_exceptions=(subprocess.CalledProcessError, ConnectionError, TimeoutError)
    )
    
    return success


def git_pull_with_retry(
    repo_dir: str,
    max_retries: int = 3
) -> bool:
    """Pull latest changes with retry logic.
    
    Args:
        repo_dir: Repository directory
        max_retries: Maximum retry attempts
    
    Returns:
        True if successful
    """
    def pull_operation():
        result = subprocess.run(
            ["git", "-C", repo_dir, "pull"],
            check=True,
            capture_output=True,
            text=True
        )
        return result
    
    success, result = retry_with_backoff(
        pull_operation,
        max_retries=max_retries,
        retry_on_exceptions=(subprocess.CalledProcessError, ConnectionError, TimeoutError)
    )
    
    return success

