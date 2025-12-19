"""Unit tests for compliance utilities."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from meta.utils.compliance import generate_compliance_report, export_compliance_report


class TestCompliance:
    """Tests for compliance utilities."""
    
    @patch('meta.utils.compliance.check_component_health')
    @patch('meta.utils.compliance.check_license_compliance')
    @patch('meta.utils.compliance.scan_vulnerabilities')
    @patch('meta.utils.compliance.check_policies')
    def test_generate_compliance_report(self, mock_policies, mock_security, mock_license, mock_health):
        """Test generating compliance report."""
        mock_health.return_value = {"healthy": True}
        mock_license.return_value = {"compliant": True}
        mock_security.return_value = {"safe": True}
        mock_policies.return_value = {"compliant": True}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manifests_dir = Path(tmpdir) / "manifests"
            manifests_dir.mkdir()
            
            components_yaml = manifests_dir / "components.yaml"
            components_yaml.write_text("""
components:
  test-component:
    type: service
    version: v1.0.0
""")
            
            report = generate_compliance_report(manifests_dir=str(manifests_dir))
            assert "summary" in report
            assert "components" in report
            assert report["summary"]["total"] == 1


