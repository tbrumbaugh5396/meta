# Interface Contracts

This document defines the stable interfaces for all components in the meta-repo system.

## Contract Principles

1. **Stability**: Interfaces must remain stable across minor version bumps
2. **Versioning**: Breaking changes require major version bumps
3. **Documentation**: All interfaces must be fully documented
4. **Testing**: Contract tests validate interface compliance

## Component Interfaces

### infrastructure-primitives

**Location:** `infrastructure-primitives/contracts/infrastructure_interface.py`

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List

class ProxyInterface(ABC):
    """Proxy management interface."""
    
    @abstractmethod
    async def get_proxy(self, region: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get an available proxy."""
        pass

class StorageInterface(ABC):
    """Storage interface."""
    
    @abstractmethod
    async def store(self, key: str, value: bytes) -> bool:
        """Store data."""
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[bytes]:
        """Retrieve data."""
        pass

class MessagingInterface(ABC):
    """Messaging interface."""
    
    @abstractmethod
    async def publish(self, topic: str, message: Dict[str, Any]) -> bool:
        """Publish message to topic."""
        pass
    
    @abstractmethod
    async def subscribe(self, topic: str, callback: callable) -> None:
        """Subscribe to topic."""
        pass
```

### agent-core

**Location:** `agent-core/contracts/agent_interface.py`

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class AgentInterface(ABC):
    """Agent intelligence interface."""
    
    @abstractmethod
    async def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make a decision based on context."""
        pass
    
    @abstractmethod
    async def generate_plan(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """Generate execution plan from goal."""
        pass
    
    @abstractmethod
    async def observe(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Observe and update internal state."""
        pass
```

### scraper-capabilities

**Location:** `scraper-capabilities/contracts/scraper_interface.py`

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class ScraperInterface(ABC):
    """Scraper interface."""
    
    @abstractmethod
    async def scrape(self, url: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape a URL with given configuration."""
        pass
    
    @abstractmethod
    async def extract(self, content: bytes, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract data from content using selectors."""
        pass
```

### workflow-engine

**Location:** `workflow-engine/contracts/workflow_interface.py`

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class WorkflowExecutorInterface(ABC):
    """Workflow execution interface."""
    
    @abstractmethod
    async def execute(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow definition."""
        pass
    
    @abstractmethod
    async def get_status(self, execution_id: str) -> Dict[str, Any]:
        """Get execution status."""
        pass
```

---

## Contract Testing

Each component must include contract tests that validate:

1. Interface compliance
2. Input/output validation
3. Error handling
4. Performance characteristics

Example contract test:

```python
def test_agent_interface_compliance():
    """Test that agent implementation complies with interface."""
    agent = AgentImplementation()
    assert isinstance(agent, AgentInterface)
    
    # Test all required methods exist
    assert hasattr(agent, 'decide')
    assert hasattr(agent, 'generate_plan')
    assert hasattr(agent, 'observe')
```

---

## Version Compatibility

### Minor Version (v1.0.0 → v1.1.0)
- Can add new methods
- Can add optional parameters
- Cannot remove methods
- Cannot change method signatures

### Major Version (v1.0.0 → v2.0.0)
- Can break interface
- Must document all changes
- Must provide migration guide


