"""Error recovery utilities."""

import time
from typing import Callable, Any, Optional, Dict
from functools import wraps
from meta.utils.logger import log, error, success


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0,
          exceptions: tuple = (Exception,)):
    """Retry decorator with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        error(f"Failed after {max_attempts} attempts: {e}")
                        raise
                    
                    log(f"Attempt {attempt}/{max_attempts} failed: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return None
        return wrapper
    return decorator


def with_error_recovery(func: Callable, max_retries: int = 3,
                       continue_on_error: bool = False,
                       on_error: Optional[Callable] = None) -> Callable:
    """Wrap function with error recovery."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < max_retries - 1:
                    log(f"Error on attempt {attempt + 1}/{max_retries}: {e}. Retrying...")
                    time.sleep(1.0 * (attempt + 1))  # Exponential backoff
                else:
                    if continue_on_error:
                        error(f"Error after {max_retries} attempts: {e}. Continuing...")
                        if on_error:
                            on_error(e, *args, **kwargs)
                        return None
                    else:
                        raise
        return None
    return wrapper


class ErrorRecoveryContext:
    """Context manager for error recovery."""
    
    def __init__(self, max_retries: int = 3, continue_on_error: bool = False,
                 on_error: Optional[Callable] = None):
        self.max_retries = max_retries
        self.continue_on_error = continue_on_error
        self.on_error = on_error
        self.errors: list = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and not self.continue_on_error:
            return False  # Re-raise exception
        
        if exc_type:
            self.errors.append(exc_val)
            if self.on_error:
                self.on_error(exc_val)
        
        return self.continue_on_error  # Suppress exception if continue_on_error


def execute_with_recovery(operations: list, max_retries: int = 3,
                         continue_on_error: bool = False) -> Dict[str, Any]:
    """Execute multiple operations with error recovery."""
    results = {
        "successful": [],
        "failed": [],
        "errors": []
    }
    
    for op in operations:
        name = op.get("name", "unknown")
        func = op.get("func")
        args = op.get("args", [])
        kwargs = op.get("kwargs", {})
        
        if not func:
            continue
        
        try:
            with ErrorRecoveryContext(max_retries, continue_on_error):
                result = func(*args, **kwargs)
                results["successful"].append({"name": name, "result": result})
        except Exception as e:
            results["failed"].append({"name": name, "error": str(e)})
            results["errors"].append(e)
            if not continue_on_error:
                break
    
    return results


