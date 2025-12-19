"""Unit tests for deployment utilities."""

import pytest
from unittest.mock import patch, MagicMock
from meta.utils.deployment import DeploymentManager, get_deployment_manager


class TestDeploymentManager:
    """Tests for DeploymentManager."""
    
    @patch('meta.utils.deployment.checkout_version')
    @patch('meta.utils.deployment.check_component_health')
    def test_deploy_immediate(self, mock_health, mock_checkout):
        """Test immediate deployment."""
        mock_health.return_value = {"healthy": True}
        mock_checkout.return_value = True
        
        manager = DeploymentManager()
        result = manager.deploy("test-component", "v1.0.0", "immediate")
        
        assert result is True
        mock_checkout.assert_called_once()
    
    @patch('meta.utils.deployment.checkout_version')
    @patch('meta.utils.deployment.check_component_health')
    def test_deploy_blue_green(self, mock_health, mock_checkout):
        """Test blue-green deployment."""
        mock_health.return_value = {"healthy": True}
        mock_checkout.return_value = True
        
        manager = DeploymentManager()
        result = manager.deploy("test-component", "v1.0.0", "blue-green", instances=2)
        
        assert result is True
        mock_checkout.assert_called()
        mock_health.assert_called()
    
    @patch('meta.utils.deployment.checkout_version')
    @patch('meta.utils.deployment.check_component_health')
    def test_deploy_canary(self, mock_health, mock_checkout):
        """Test canary deployment."""
        mock_health.return_value = {"healthy": True}
        mock_checkout.return_value = True
        
        manager = DeploymentManager()
        result = manager.deploy("test-component", "v1.0.0", "canary", canary_percentage=10, instances=10)
        
        assert result is True
        mock_checkout.assert_called()
        mock_health.assert_called()


