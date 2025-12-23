"""Unit tests for dependency resolution and validation."""

import pytest
from meta.utils.dependencies import (
    get_component_dependencies,
    resolve_transitive_dependencies,
    validate_dependencies,
    get_dependency_order
)


class TestDependencyResolution:
    """Tests for dependency resolution."""
    
    def test_get_component_dependencies(self):
        """Test getting direct dependencies for a component."""
        components = {
            "component-a": {
                "depends_on": ["component-b", "component-c"]
            },
            "component-b": {
                "depends_on": []
            },
            "component-c": {
                "depends_on": []
            }
        }
        
        deps = get_component_dependencies("component-a", components)
        
        assert "component-b" in deps
        assert "component-c" in deps
        assert len(deps) == 2
    
    def test_get_component_dependencies_none(self):
        """Test getting dependencies for component with no dependencies."""
        components = {
            "component-a": {
                "depends_on": []
            }
        }
        
        deps = get_component_dependencies("component-a", components)
        
        assert len(deps) == 0
    
    def test_resolve_transitive_dependencies(self):
        """Test resolving transitive dependencies."""
        components = {
            "component-a": {
                "depends_on": ["component-b"]
            },
            "component-b": {
                "depends_on": ["component-c"]
            },
            "component-c": {
                "depends_on": []
            }
        }
        
        deps = resolve_transitive_dependencies("component-a", components)
        
        # Should include both direct and transitive
        assert "component-b" in deps
        assert "component-c" in deps
    
    def test_resolve_transitive_dependencies_no_cycles(self):
        """Test that transitive resolution handles cycles gracefully."""
        components = {
            "component-a": {
                "depends_on": ["component-b"]
            },
            "component-b": {
                "depends_on": ["component-a"]  # Cycle
            }
        }
        
        # Should not infinite loop
        deps = resolve_transitive_dependencies("component-a", components)
        
        # Should at least return direct dependency
        assert "component-b" in deps
    
    def test_validate_dependencies_all_exist(self, monkeypatch):
        """Test validation when all dependencies exist."""
        monkeypatch.setattr('meta.utils.dependencies.get_components', lambda x: {
            "component-a": {
                "depends_on": ["component-b"]
            },
            "component-b": {
                "depends_on": []
            }
        })
        
        valid, errors = validate_dependencies()
        
        assert valid is True
        assert len(errors) == 0
    
    def test_validate_dependencies_missing(self, monkeypatch):
        """Test validation when dependencies are missing."""
        monkeypatch.setattr('meta.utils.dependencies.get_components', lambda x: {
            "component-a": {
                "depends_on": ["component-b", "component-c"]
            },
            "component-b": {
                "depends_on": []
            }
            # component-c is missing
        })
        
        valid, errors = validate_dependencies()
        
        assert valid is False
        assert len(errors) > 0
        assert any("component-c" in error for error in errors)
    
    def test_validate_dependencies_cycles(self, monkeypatch):
        """Test validation detects circular dependencies."""
        monkeypatch.setattr('meta.utils.dependencies.get_components', lambda x: {
            "component-a": {
                "depends_on": ["component-b"]
            },
            "component-b": {
                "depends_on": ["component-a"]  # Cycle
            }
        })
        
        valid, errors = validate_dependencies()
        
        assert valid is False
        assert len(errors) > 0
        assert any("circular" in error.lower() or "cycle" in error.lower() for error in errors)
    
    def test_get_dependency_order(self):
        """Test getting components in dependency order."""
        components = {
            "component-a": {
                "depends_on": ["component-b"]
            },
            "component-b": {
                "depends_on": ["component-c"]
            },
            "component-c": {
                "depends_on": []
            }
        }
        
        order = get_dependency_order(components)
        
        # component-c should come before component-b
        # component-b should come before component-a
        # Note: topological sort may vary, but dependencies should be respected
        assert "component-c" in order
        assert "component-b" in order
        assert "component-a" in order
        # Verify dependency order: component-c has no deps, component-b depends on c, 
        # component-a depends on b. So order should be: c, b, a (or any valid topological order)
        # The key constraint: if A depends on B, B must come before A
        assert order.index("component-c") < order.index("component-b")
        assert order.index("component-b") < order.index("component-a")
    
    def test_get_dependency_order_no_deps(self):
        """Test dependency order with no dependencies."""
        components = {
            "component-a": {
                "depends_on": []
            },
            "component-b": {
                "depends_on": []
            }
        }
        
        order = get_dependency_order(components)
        
        # Should include all components
        assert "component-a" in order
        assert "component-b" in order
        assert len(order) == 2

