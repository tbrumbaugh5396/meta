"""Tests for vendor commands."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from typer.testing import CliRunner
from meta.cli import app


class TestVendorCommand:
    """Test vendor command group."""
    
    def test_vendor_import_component(self, temp_meta_repo, mock_vendor):
        """Test importing a single component."""
        runner = CliRunner()
        
        with patch("meta.commands.vendor.is_vendored_mode", return_value=True), \
             patch("meta.commands.vendor.get_components", return_value={
                 "test-component": {
                     "repo": "git@github.com:test/test.git",
                     "version": "v1.0.0"
                 }
             }), \
             patch("meta.commands.vendor.vendor_component", return_value=True):
            
            result = runner.invoke(app, [
                "vendor", "import-component", "test-component"
            ])
            
            assert result.exit_code == 0
    
    def test_vendor_import_all(self, temp_meta_repo, mock_vendor):
        """Test importing all components."""
        runner = CliRunner()
        
        with patch("meta.commands.vendor.is_vendored_mode", return_value=True), \
             patch("meta.commands.vendor.get_components", return_value={
                 "test-component": {
                     "repo": "git@github.com:test/test.git",
                     "version": "v1.0.0"
                 }
             }), \
             patch("meta.commands.vendor.vendor_component", return_value=True):
            
            result = runner.invoke(app, ["vendor", "import-all"])
            
            assert result.exit_code == 0
    
    def test_vendor_status(self, temp_meta_repo, mock_vendor):
        """Test vendor status command."""
        runner = CliRunner()
        
        with patch("meta.commands.vendor.is_vendored_mode", return_value=True), \
             patch("meta.commands.vendor.get_components", return_value={
                 "test-component": {
                     "repo": "git@github.com:test/test.git",
                     "version": "v1.0.0"
                 }
             }), \
             patch("meta.commands.vendor.find_meta_repo_root", return_value=temp_meta_repo["path"]), \
             patch("meta.commands.vendor.get_vendor_info", return_value={
                 "version": "v1.0.0",
                 "vendored_at": "2024-01-15T10:30:00Z"
             }), \
             patch("pathlib.Path.exists", return_value=True):
            
            result = runner.invoke(app, ["vendor", "status"])
            
            assert result.exit_code == 0
    
    def test_vendor_convert_to_vendored(self, temp_meta_repo, mock_vendor):
        """Test converting to vendored mode."""
        runner = CliRunner()
        
        with patch("meta.commands.vendor.convert_to_vendored_mode_enhanced", return_value=(True, {'successful': ['comp1']})):
            result = runner.invoke(app, ["vendor", "convert", "vendored"])
            
            assert result.exit_code == 0
    
    def test_vendor_convert_to_reference(self, temp_meta_repo, mock_vendor):
        """Test converting to reference mode."""
        runner = CliRunner()
        
        with patch("meta.commands.vendor.convert_to_reference_mode", return_value=True):
            result = runner.invoke(app, ["vendor", "convert", "reference"])
            
            assert result.exit_code == 0
    
    def test_vendor_convert_invalid_mode(self, temp_meta_repo, mock_vendor):
        """Test converting with invalid mode."""
        runner = CliRunner()
        
        result = runner.invoke(app, ["vendor", "convert", "invalid"])
        
        assert result.exit_code == 1
    
    def test_vendor_release(self, temp_meta_repo, mock_vendor):
        """Test production release command."""
        runner = CliRunner()
        
        with patch("meta.utils.vendor.convert_to_vendored_for_production", return_value=True), \
             patch("meta.utils.git.git_available", return_value=True), \
             patch("subprocess.run", return_value=MagicMock()):
            
            result = runner.invoke(app, [
                "vendor", "release", "--env", "prod", "--version", "v1.0.0"
            ])
            
            assert result.exit_code == 0
    
    def test_vendor_release_no_version(self, temp_meta_repo, mock_vendor):
        """Test production release without version tag."""
        runner = CliRunner()
        
        with patch("meta.commands.vendor.convert_to_vendored_for_production", return_value=True):
            result = runner.invoke(app, ["vendor", "release", "--env", "prod"])
            
            assert result.exit_code == 0
    
    def test_vendor_import_component_not_vendored_mode(self, temp_meta_repo, mock_vendor):
        """Test importing component when not in vendored mode."""
        runner = CliRunner()
        
        with patch("meta.commands.vendor.is_vendored_mode", return_value=False):
            result = runner.invoke(app, [
                "vendor", "import-component", "test-component"
            ])
            
            assert result.exit_code == 1
    
    def test_vendor_status_not_vendored_mode(self, temp_meta_repo, mock_vendor):
        """Test status command when not in vendored mode."""
        runner = CliRunner()
        
        with patch("meta.commands.vendor.is_vendored_mode", return_value=False):
            result = runner.invoke(app, ["vendor", "status"])
            
            assert result.exit_code == 1
    
    def test_vendor_convert_with_dry_run(self, temp_meta_repo, mock_vendor):
        """Test convert command with dry-run."""
        runner = CliRunner()
        
        with patch("meta.commands.vendor.convert_to_vendored_mode_enhanced", return_value=(True, {'dry_run': True})):
            result = runner.invoke(app, ["vendor", "convert", "vendored", "--dry-run"])
            
            assert result.exit_code == 0
    
    def test_vendor_convert_with_continue_on_error(self, temp_meta_repo, mock_vendor):
        """Test convert command with continue-on-error."""
        runner = CliRunner()
        
        with patch("meta.commands.vendor.convert_to_vendored_mode_enhanced", return_value=(True, {'successful': ['comp1'], 'failed': ['comp2']})):
            result = runner.invoke(app, ["vendor", "convert", "vendored", "--continue-on-error"])
            
            assert result.exit_code == 0
    
    def test_vendor_verify(self, temp_meta_repo, mock_vendor):
        """Test verify command."""
        runner = CliRunner()
        
        with patch("meta.commands.vendor.verify_conversion", return_value=(True, {'components_valid': 1, 'components_checked': 1})):
            result = runner.invoke(app, ["vendor", "verify"])
            
            assert result.exit_code == 0
    
    def test_vendor_backup(self, temp_meta_repo, mock_vendor):
        """Test backup command."""
        runner = CliRunner()
        
        backup_path = temp_meta_repo["path"] / ".meta" / "backups" / "test-backup"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        with patch("meta.utils.vendor_backup.create_backup", return_value=backup_path):
            result = runner.invoke(app, ["vendor", "backup", "--name", "test-backup"])
            
            assert result.exit_code == 0
    
    def test_vendor_list_backups(self, temp_meta_repo, mock_vendor):
        """Test list-backups command."""
        runner = CliRunner()
        
        with patch("meta.commands.vendor.list_backups", return_value=[]):
            result = runner.invoke(app, ["vendor", "list-backups"])
            
            assert result.exit_code == 0
    
    def test_vendor_resume(self, temp_meta_repo, mock_vendor):
        """Test resume command."""
        runner = CliRunner()
        
        mock_checkpoint = MagicMock()
        mock_checkpoint.checkpoint_id = "checkpoint-123"
        
        with patch("meta.utils.vendor_resume.resume_conversion", return_value=mock_checkpoint), \
             patch("meta.commands.vendor.convert_to_vendored_mode_enhanced", return_value=(True, {'successful': ['comp1']})):
            result = runner.invoke(app, ["vendor", "resume"])
            
            assert result.exit_code == 0
    
    def test_vendor_list_checkpoints(self, temp_meta_repo, mock_vendor):
        """Test list-checkpoints command."""
        runner = CliRunner()
        
        with patch("meta.commands.vendor.list_checkpoints", return_value=[]):
            result = runner.invoke(app, ["vendor", "list-checkpoints"])
            
            assert result.exit_code == 0

