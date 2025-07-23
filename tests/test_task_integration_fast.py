"""
Fast Integration tests for AWDX Task Module

Uses mocking instead of subprocess for faster execution.
"""

import os
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from src.awdx.task.task_commands import app as task_app


@pytest.fixture
def runner():
    return CliRunner()


@pytest.mark.integration
@pytest.mark.task
class TestTaskIntegrationFast:
    """Fast integration tests using mocking."""

    def test_task_module_help(self, runner):
        """Test that task module help works correctly"""
        result = runner.invoke(task_app, ["--help"])
        
        assert result.exit_code == 0
        assert "High-level DevSecOps task automation" in result.stdout
        assert "security-audit" in result.stdout
        assert "cost-optimize" in result.stdout

    def test_task_help_command(self, runner):
        """Test the detailed help command"""
        result = runner.invoke(task_app, ["help"])
        
        assert result.exit_code == 0
        assert "AWDX Task Module" in result.stdout
        assert "Available Commands" in result.stdout

    def test_security_audit_help(self, runner):
        """Test security audit help"""
        result = runner.invoke(task_app, ["security-audit", "--help"])
        
        assert result.exit_code == 0
        assert "comprehensive security audit" in result.stdout
        assert "--comprehensive" in result.stdout
        assert "--fix-safe" in result.stdout

    def test_cost_optimize_help(self, runner):
        """Test cost optimize help"""
        result = runner.invoke(task_app, ["cost-optimize", "--help"])
        
        assert result.exit_code == 0
        assert "optimize AWS costs" in result.stdout
        assert "--auto-fix" in result.stdout
        assert "--dry-run" in result.stdout

    def test_compliance_check_help(self, runner):
        """Test compliance check help"""
        result = runner.invoke(task_app, ["compliance-check", "--help"])
        
        assert result.exit_code == 0
        assert "compliance checks" in result.stdout
        assert "--framework" in result.stdout
        assert "--quick" in result.stdout

    def test_security_monitor_help(self, runner):
        """Test security monitor help"""
        result = runner.invoke(task_app, ["security-monitor", "--help"])
        
        assert result.exit_code == 0
        assert "security monitoring" in result.stdout
        assert "--continuous" in result.stdout
        assert "--alert" in result.stdout

    def test_secret_rotate_help(self, runner):
        """Test secret rotate help"""
        result = runner.invoke(task_app, ["secret-rotate", "--help"])
        
        assert result.exit_code == 0
        assert "secret rotation" in result.stdout
        assert "--auto" in result.stdout
        assert "--schedule" in result.stdout

    def test_vuln_scan_help(self, runner):
        """Test vulnerability scan help"""
        result = runner.invoke(task_app, ["vuln-scan", "--help"])
        
        assert result.exit_code == 0
        assert "vulnerability scanning" in result.stdout
        assert "--auto-remediate" in result.stdout
        assert "--low-risk" in result.stdout

    @patch('boto3.Session')
    def test_task_module_without_aws_credentials(self, mock_session, runner):
        """Test task module gracefully handles missing AWS credentials"""
        # Mock boto3 to simulate missing credentials
        mock_session.side_effect = Exception("No credentials found")
        
        result = runner.invoke(task_app, ["security-audit"])
        
        # Should fail gracefully with clear error message
        assert result.exit_code == 1
        assert "Security audit failed" in result.stdout

    def test_task_module_invalid_command(self, runner):
        """Test task module handles invalid commands gracefully"""
        result = runner.invoke(task_app, ["invalid-command"])
        
        assert result.exit_code == 2  # Typer error code for invalid command
        # Check stdout instead of stderr since stderr is not separately captured
        assert "No such command" in result.stdout or "Error" in result.stdout

    @patch('boto3.Session')
    def test_task_module_with_verbose(self, mock_session, runner):
        """Test task module with verbose flag"""
        # Mock boto3 to simulate missing credentials
        mock_session.side_effect = Exception("No credentials found")
        
        result = runner.invoke(task_app, ["security-audit", "--verbose"])
        
        # Should fail due to AWS credentials, but verbose flag should be accepted
        assert result.exit_code == 1
        assert "Security audit failed" in result.stdout

    @patch('boto3.Session')
    def test_task_module_with_region(self, mock_session, runner):
        """Test task module with region parameter"""
        # Mock boto3 to simulate missing credentials
        mock_session.side_effect = Exception("No credentials found")
        
        result = runner.invoke(task_app, ["security-audit", "--region", "us-east-1"])
        
        # Should fail due to AWS credentials, but region flag should be accepted
        assert result.exit_code == 1
        assert "Security audit failed" in result.stdout

    def test_task_module_output_formats(self, runner):
        """Test task module accepts different output formats"""
        # Test JSON output
        result = runner.invoke(task_app, ["security-audit", "--output", "json"])
        assert result.exit_code == 1  # Should fail due to AWS credentials
        
        # Test YAML output
        result = runner.invoke(task_app, ["security-audit", "--output", "yaml"])
        assert result.exit_code == 1  # Should fail due to AWS credentials
        
        # Test CSV output
        result = runner.invoke(task_app, ["security-audit", "--output", "csv"])
        assert result.exit_code == 1  # Should fail due to AWS credentials

    @patch('boto3.Session')
    def test_task_module_comprehensive_flag(self, mock_session, runner):
        """Test task module with comprehensive flag"""
        # Mock boto3 to simulate missing credentials
        mock_session.side_effect = Exception("No credentials found")
        
        result = runner.invoke(task_app, ["security-audit", "--comprehensive"])
        
        # Should fail due to AWS credentials, but comprehensive flag should be accepted
        assert result.exit_code == 1
        assert "Security audit failed" in result.stdout

    @patch('boto3.Session')
    def test_task_module_fix_safe_flag(self, mock_session, runner):
        """Test task module with fix-safe flag"""
        # Mock boto3 to simulate missing credentials
        mock_session.side_effect = Exception("No credentials found")
        
        result = runner.invoke(task_app, ["security-audit", "--fix-safe"])
        
        # Should fail due to AWS credentials, but fix-safe flag should be accepted
        assert result.exit_code == 1
        assert "Security audit failed" in result.stdout

    @patch('boto3.Session')
    def test_cost_optimize_dry_run(self, mock_session, runner):
        """Test cost optimize with dry-run flag"""
        # Mock boto3 to simulate missing credentials
        mock_session.side_effect = Exception("No credentials found")
        
        result = runner.invoke(task_app, ["cost-optimize", "--dry-run"])
        
        # Should fail due to AWS credentials, but dry-run flag should be accepted
        assert result.exit_code == 1
        assert "Cost optimization failed" in result.stdout

    @patch('boto3.Session')
    def test_cost_optimize_auto_fix(self, mock_session, runner):
        """Test cost optimize with auto-fix flag"""
        # Mock boto3 to simulate missing credentials
        mock_session.side_effect = Exception("No credentials found")
        
        result = runner.invoke(task_app, ["cost-optimize", "--auto-fix"])
        
        # Should fail due to AWS credentials, but auto-fix flag should be accepted
        assert result.exit_code == 1
        assert "Cost optimization failed" in result.stdout

    @patch('boto3.Session')
    def test_compliance_check_frameworks(self, mock_session, runner):
        """Test compliance check with different frameworks"""
        # Mock boto3 to simulate missing credentials
        mock_session.side_effect = Exception("No credentials found")
        
        # Test SOX framework
        result = runner.invoke(task_app, ["compliance-check", "--framework", "sox"])
        assert result.exit_code == 1
        
        # Test HIPAA framework
        result = runner.invoke(task_app, ["compliance-check", "--framework", "hipaa"])
        assert result.exit_code == 1
        
        # Test PCI framework
        result = runner.invoke(task_app, ["compliance-check", "--framework", "pci"])
        assert result.exit_code == 1

    @patch('boto3.Session')
    def test_security_monitor_continuous(self, mock_session, runner):
        """Test security monitor with continuous flag"""
        # Mock boto3 to simulate missing credentials
        mock_session.side_effect = Exception("No credentials found")
        
        result = runner.invoke(task_app, ["security-monitor", "--continuous"])
        
        # Should fail due to AWS credentials, but continuous flag should be accepted
        assert result.exit_code == 1
        assert "Security monitoring failed" in result.stdout

    @patch('boto3.Session')
    def test_secret_rotate_auto(self, mock_session, runner):
        """Test secret rotate with auto flag"""
        # Mock boto3 to simulate missing credentials
        mock_session.side_effect = Exception("No credentials found")
        
        result = runner.invoke(task_app, ["secret-rotate", "--auto"])
        
        # Should fail due to AWS credentials, but auto flag should be accepted
        assert result.exit_code == 1
        assert "Secret rotation failed" in result.stdout

    @patch('boto3.Session')
    def test_vuln_scan_auto_remediate(self, mock_session, runner):
        """Test vulnerability scan with auto-remediate flag"""
        # Mock boto3 to simulate missing credentials
        mock_session.side_effect = Exception("No credentials found")
        
        result = runner.invoke(task_app, ["vuln-scan", "--auto-remediate"])
        
        # Should fail due to AWS credentials, but auto-remediate flag should be accepted
        assert result.exit_code == 1
        assert "Vulnerability scan failed" in result.stdout 