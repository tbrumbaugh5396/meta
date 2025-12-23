"""Dependency injection container for testing."""
from typing import Dict, Any, Callable, Optional
from unittest.mock import MagicMock


class DIContainer:
    """Dependency injection container for tests."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
    
    def register(self, name: str, service: Any):
        """Register a service instance."""
        self._services[name] = service
    
    def register_factory(self, name: str, factory: Callable):
        """Register a factory function."""
        self._factories[name] = factory
    
    def get(self, name: str) -> Any:
        """Get a service, creating if factory exists."""
        if name in self._services:
            return self._services[name]
        if name in self._factories:
            service = self._factories[name]()
            self._services[name] = service
            return service
        raise KeyError(f"Service '{name}' not found")
    
    def mock(self, name: str) -> MagicMock:
        """Create and register a mock service."""
        mock = MagicMock()
        self.register(name, mock)
        return mock
    
    def clear(self):
        """Clear all registered services."""
        self._services.clear()
        self._factories.clear()


