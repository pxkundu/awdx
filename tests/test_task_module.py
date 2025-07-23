"""
Comprehensive tests for AWDX Task Module

Tests all task commands, edge cases, error handling, and user experience scenarios.
"""

import json
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import boto3
import pytest
from botocore.exceptions import ClientError, EndpointConnectionError, NoCredentialsError
from rich.console import Console
from typer.testing import CliRunner

from src.awdx.task.task_commands import (
    analyze_cache_costs,
    analyze_current_costs,
    analyze_ec2_costs,
    analyze_rds_costs,
)
from src.awdx.task.task_commands import app as task_app
from src.awdx.task.task_commands import (
    audit_ec2_security,
    audit_iam_security,
    audit_s3_security,
    audit_secrets_security,
    check_compliance_framework,
    list_secrets_for_rotation,
    rotate_specific_secret,
    run_security_monitoring,
    scan_ec2_vulnerabilities,
    scan_lambda_vulnerabilities,
    scan_rds_vulnerabilities,
    scan_s3_vulnerabilities,
)


# Test fixtures
@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_aws_session():
    """Mock AWS session for testing"""
    with patch("boto3.Session") as mock_session:
        session = Mock()
        mock_session.return_value = session
        yield session


@pytest.fixture
def mock_iam_client():
    """Mock IAM client"""
    client = Mock()
    client.list_users.return_value = {
        "Users": [
            {"UserName": "test-user-1", "CreateDate": datetime.now()},
            {"UserName": "test-user-2", "CreateDate": datetime.now()},
        ]
    }
    client.list_roles.return_value = {
        "Roles": [{"RoleName": "test-role-1"}, {"RoleName": "test-role-2"}]
    }
    client.list_policies.return_value = {
        "Policies": [{"PolicyName": "test-policy-1"}, {"PolicyName": "test-policy-2"}]
    }
    return client


@pytest.fixture
def mock_ec2_client():
    """Mock EC2 client"""
    client = Mock()
    client.describe_instances.return_value = {
        "Reservations": [
            {
                "Instances": [
                    {
                        "InstanceId": "i-1234567890abcdef0",
                        "InstanceType": "t3.micro",
                        "State": {"Name": "running"},
                        "SecurityGroups": [{"GroupName": "default"}],
                        "BlockDeviceMappings": [],
                    }
                ]
            }
        ]
    }
    client.describe_security_groups.return_value = {
        "SecurityGroups": [
            {
                "GroupName": "default",
                "GroupId": "sg-12345678",
                "IpPermissions": [],
                "IpPermissionsEgress": [],
            }
        ]
    }
    return client


@pytest.fixture
def mock_s3_client():
    """Mock S3 client"""
    client = Mock()
    client.list_buckets.return_value = {
        "Buckets": [
            {"Name": "test-bucket-1", "CreationDate": datetime.now()},
            {"Name": "test-bucket-2", "CreationDate": datetime.now()},
        ]
    }
    client.get_bucket_encryption.side_effect = ClientError(
        {"Error": {"Code": "ServerSideEncryptionConfigurationNotFoundError"}},
        "GetBucketEncryption",
    )
    return client


@pytest.fixture
def mock_secrets_client():
    """Mock Secrets Manager client"""
    client = Mock()
    client.list_secrets.return_value = {
        "SecretList": [
            {
                "Name": "test-secret-1",
                "LastModifiedDate": datetime.now(),
                "RotationEnabled": False,
            },
            {
                "Name": "test-secret-2",
                "LastModifiedDate": datetime.now(),
                "RotationEnabled": True,
            },
        ]
    }
    return client


@pytest.fixture
def mock_ce_client():
    """Mock Cost Explorer client"""
    client = Mock()
    client.get_cost_and_usage.return_value = {
        "ResultsByTime": [
            {
                "TimePeriod": {"Start": "2024-01-01", "End": "2024-01-02"},
                "Total": {"BlendedCost": {"Amount": "100.00", "Unit": "USD"}},
            }
        ]
    }
    return client


@pytest.mark.integration
@pytest.mark.task
class TestSecurityAudit:
    """Test security audit functionality"""

    def test_security_audit_basic(
        self,
        runner,
        mock_aws_session,
        mock_iam_client,
        mock_ec2_client,
        mock_s3_client,
        mock_secrets_client,
    ):
        """Test basic security audit command"""
        mock_aws_session.client.side_effect = [
            mock_iam_client,
            mock_ec2_client,
            mock_s3_client,
            mock_secrets_client,
        ]

        result = runner.invoke(task_app, ["security-audit"])
        assert result.exit_code == 0
        assert "Security audit completed" in result.stdout

    def test_security_audit_comprehensive(
        self,
        runner,
        mock_aws_session,
        mock_iam_client,
        mock_ec2_client,
        mock_s3_client,
        mock_secrets_client,
    ):
        """Test comprehensive security audit"""
        mock_aws_session.client.side_effect = [
            mock_iam_client,
            mock_ec2_client,
            mock_s3_client,
            mock_secrets_client,
        ]

        result = runner.invoke(task_app, ["security-audit", "--comprehensive"])
        assert result.exit_code == 0
        assert "Security audit completed" in result.stdout

    def test_security_audit_with_fix_safe(
        self,
        runner,
        mock_aws_session,
        mock_iam_client,
        mock_ec2_client,
        mock_s3_client,
        mock_secrets_client,
    ):
        """Test security audit with auto-fix"""
        mock_aws_session.client.side_effect = [
            mock_iam_client,
            mock_ec2_client,
            mock_s3_client,
            mock_secrets_client,
        ]

        result = runner.invoke(task_app, ["security-audit", "--fix-safe"])
        assert result.exit_code == 0
        assert "Security audit completed" in result.stdout

    def test_security_audit_aws_error(self, runner, mock_aws_session):
        """Test security audit with AWS error"""
        mock_aws_session.client.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "DescribeInstances",
        )

        result = runner.invoke(task_app, ["security-audit"])
        assert result.exit_code == 1
        assert "Security audit failed" in result.stdout

    def test_security_audit_no_credentials(self, runner):
        """Test security audit without AWS credentials"""
        with patch("boto3.Session") as mock_session:
            mock_session.side_effect = NoCredentialsError()

            result = runner.invoke(task_app, ["security-audit"])
            assert result.exit_code == 1
            assert "Security audit failed" in result.stdout


@pytest.mark.integration
@pytest.mark.task
class TestCostOptimize:
    """Test cost optimization functionality"""

    def test_cost_optimize_basic(
        self, runner, mock_aws_session, mock_ce_client, mock_ec2_client, mock_s3_client
    ):
        """Test basic cost optimization"""
        mock_aws_session.client.side_effect = [
            mock_ce_client,
            mock_ec2_client,
            mock_s3_client,
        ]

        result = runner.invoke(task_app, ["cost-optimize"])
        assert result.exit_code == 0
        assert "Cost optimization completed" in result.stdout

    def test_cost_optimize_dry_run(
        self, runner, mock_aws_session, mock_ce_client, mock_ec2_client, mock_s3_client
    ):
        """Test cost optimization with dry run"""
        mock_aws_session.client.side_effect = [
            mock_ce_client,
            mock_ec2_client,
            mock_s3_client,
        ]

        result = runner.invoke(task_app, ["cost-optimize", "--dry-run"])
        assert result.exit_code == 0
        assert "Cost optimization completed" in result.stdout

    def test_cost_optimize_auto_fix(
        self, runner, mock_aws_session, mock_ce_client, mock_ec2_client, mock_s3_client
    ):
        """Test cost optimization with auto-fix"""
        mock_aws_session.client.side_effect = [
            mock_ce_client,
            mock_ec2_client,
            mock_s3_client,
        ]

        result = runner.invoke(task_app, ["cost-optimize", "--auto-fix"])
        assert result.exit_code == 0
        assert "Cost optimization completed" in result.stdout

    def test_cost_optimize_custom_threshold(
        self, runner, mock_aws_session, mock_ce_client, mock_ec2_client, mock_s3_client
    ):
        """Test cost optimization with custom threshold"""
        mock_aws_session.client.side_effect = [
            mock_ce_client,
            mock_ec2_client,
            mock_s3_client,
        ]

        result = runner.invoke(task_app, ["cost-optimize", "--threshold", "20.0"])
        assert result.exit_code == 0
        assert "Cost optimization completed" in result.stdout

    def test_cost_optimize_aws_error(self, runner, mock_aws_session):
        """Test cost optimization with AWS error"""
        mock_aws_session.client.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "GetCostAndUsage",
        )

        result = runner.invoke(task_app, ["cost-optimize"])
        assert result.exit_code == 1
        assert "Cost optimization failed" in result.stdout


@pytest.mark.integration
@pytest.mark.task
class TestComplianceCheck:
    """Test compliance check functionality"""

    def test_compliance_check_all_frameworks(self, runner, mock_aws_session):
        """Test compliance check for all frameworks"""
        result = runner.invoke(task_app, ["compliance-check", "--framework", "all"])
        assert result.exit_code == 0
        assert "Compliance check completed" in result.stdout

    def test_compliance_check_sox(self, runner, mock_aws_session):
        """Test compliance check for SOX"""
        result = runner.invoke(task_app, ["compliance-check", "--framework", "sox"])
        assert result.exit_code == 0
        assert "Compliance check completed" in result.stdout

    def test_compliance_check_hipaa(self, runner, mock_aws_session):
        """Test compliance check for HIPAA"""
        result = runner.invoke(task_app, ["compliance-check", "--framework", "hipaa"])
        assert result.exit_code == 0
        assert "Compliance check completed" in result.stdout

    def test_compliance_check_quick(self, runner, mock_aws_session):
        """Test quick compliance check"""
        result = runner.invoke(task_app, ["compliance-check", "--quick"])
        assert result.exit_code == 0
        assert "Compliance check completed" in result.stdout

    def test_compliance_check_invalid_framework(self, runner, mock_aws_session):
        """Test compliance check with invalid framework"""
        result = runner.invoke(task_app, ["compliance-check", "--framework", "invalid"])
        assert result.exit_code == 0  # Should handle gracefully
        assert "Compliance check completed" in result.stdout


@pytest.mark.integration
@pytest.mark.task
class TestSecurityMonitor:
    """Test security monitoring functionality"""

    def test_security_monitor_single_run(self, runner, mock_aws_session):
        """Test single security monitoring run"""
        result = runner.invoke(task_app, ["security-monitor"])
        assert result.exit_code == 0
        assert "Security monitoring completed" in result.stdout

    def test_security_monitor_continuous(self, runner, mock_aws_session):
        """Test continuous security monitoring"""
        # Mock keyboard interrupt to stop continuous monitoring
        with patch("time.sleep", side_effect=KeyboardInterrupt()):
            result = runner.invoke(task_app, ["security-monitor", "--continuous"])
            assert "Monitoring stopped by user" in result.stdout

    def test_security_monitor_with_alerts(self, runner, mock_aws_session):
        """Test security monitoring with alerts"""
        with patch("time.sleep", side_effect=KeyboardInterrupt()):
            result = runner.invoke(
                task_app, ["security-monitor", "--continuous", "--alert"]
            )
            assert "Alerts enabled: Yes" in result.stdout

    def test_security_monitor_custom_interval(self, runner, mock_aws_session):
        """Test security monitoring with custom interval"""
        with patch("time.sleep", side_effect=KeyboardInterrupt()):
            result = runner.invoke(
                task_app, ["security-monitor", "--continuous", "--interval", "60"]
            )
            assert "Monitoring interval: 60 seconds" in result.stdout


@pytest.mark.integration
@pytest.mark.task
class TestSecretRotate:
    """Test secret rotation functionality"""

    def test_secret_rotate_basic(self, runner, mock_aws_session, mock_secrets_client):
        """Test basic secret rotation"""
        mock_aws_session.client.return_value = mock_secrets_client

        result = runner.invoke(task_app, ["secret-rotate"])
        assert result.exit_code == 0
        assert "Secret management completed" in result.stdout

    def test_secret_rotate_specific_secret(
        self, runner, mock_aws_session, mock_secrets_client
    ):
        """Test rotation of specific secret"""
        mock_aws_session.client.return_value = mock_secrets_client

        result = runner.invoke(
            task_app, ["secret-rotate", "--secret-name", "test-secret"]
        )
        assert result.exit_code == 0
        assert "Secret management completed" in result.stdout

    def test_secret_rotate_auto(self, runner, mock_aws_session, mock_secrets_client):
        """Test automatic secret rotation"""
        mock_aws_session.client.return_value = mock_secrets_client

        result = runner.invoke(task_app, ["secret-rotate", "--auto"])
        assert result.exit_code == 0
        assert "Secret management completed" in result.stdout

    def test_secret_rotate_schedule(
        self, runner, mock_aws_session, mock_secrets_client
    ):
        """Test secret rotation scheduling"""
        mock_aws_session.client.return_value = mock_secrets_client

        result = runner.invoke(task_app, ["secret-rotate", "--schedule"])
        assert result.exit_code == 0
        assert "Secret management completed" in result.stdout

    def test_secret_rotate_aws_error(self, runner, mock_aws_session):
        """Test secret rotation with AWS error"""
        mock_aws_session.client.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "ListSecrets",
        )

        result = runner.invoke(task_app, ["secret-rotate"])
        assert result.exit_code == 1
        assert "Secret rotation failed" in result.stdout


@pytest.mark.integration
@pytest.mark.task
class TestVulnScan:
    """Test vulnerability scanning functionality"""

    def test_vuln_scan_basic(self, runner, mock_aws_session):
        """Test basic vulnerability scan"""
        result = runner.invoke(task_app, ["vuln-scan"])
        assert result.exit_code == 0
        assert "Vulnerability scan completed" in result.stdout

    def test_vuln_scan_low_risk(self, runner, mock_aws_session):
        """Test vulnerability scan including low-risk"""
        result = runner.invoke(task_app, ["vuln-scan", "--low-risk"])
        assert result.exit_code == 0
        assert "Vulnerability scan completed" in result.stdout

    def test_vuln_scan_auto_remediate(self, runner, mock_aws_session):
        """Test vulnerability scan with auto-remediation"""
        result = runner.invoke(task_app, ["vuln-scan", "--auto-remediate"])
        assert result.exit_code == 0
        assert "Vulnerability scan completed" in result.stdout

    def test_vuln_scan_custom_output(self, runner, mock_aws_session):
        """Test vulnerability scan with custom output format"""
        result = runner.invoke(task_app, ["vuln-scan", "--output", "json"])
        assert result.exit_code == 0
        assert "Vulnerability scan completed" in result.stdout


@pytest.mark.integration
@pytest.mark.task
class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_no_aws_credentials(self, runner):
        """Test behavior when no AWS credentials are available"""
        with patch("boto3.Session") as mock_session:
            mock_session.side_effect = NoCredentialsError()

            result = runner.invoke(task_app, ["security-audit"])
            assert result.exit_code == 1
            assert "Security audit failed" in result.stdout

    def test_network_connection_error(self, runner, mock_aws_session):
        """Test behavior when network connection fails"""
        mock_aws_session.client.side_effect = EndpointConnectionError(
            endpoint_url="https://iam.amazonaws.com"
        )

        result = runner.invoke(task_app, ["security-audit"])
        assert result.exit_code == 1
        assert "Security audit failed" in result.stdout

    def test_permission_denied(self, runner, mock_aws_session):
        """Test behavior when AWS permissions are insufficient"""
        mock_aws_session.client.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "User is not authorized"}},
            "DescribeInstances",
        )

        result = runner.invoke(task_app, ["security-audit"])
        assert result.exit_code == 1
        assert "Security audit failed" in result.stdout

    def test_rate_limiting(self, runner, mock_aws_session):
        """Test behavior when AWS API rate limits are hit"""
        mock_aws_session.client.side_effect = ClientError(
            {"Error": {"Code": "ThrottlingException", "Message": "Rate exceeded"}},
            "DescribeInstances",
        )

        result = runner.invoke(task_app, ["security-audit"])
        assert result.exit_code == 1
        assert "Security audit failed" in result.stdout

    def test_invalid_region(self, runner, mock_aws_session):
        """Test behavior with invalid AWS region"""
        mock_aws_session.side_effect = ClientError(
            {"Error": {"Code": "InvalidParameterValue", "Message": "Invalid region"}},
            "DescribeInstances",
        )

        result = runner.invoke(
            task_app, ["security-audit", "--region", "invalid-region"]
        )
        assert result.exit_code == 1
        assert "Security audit failed" in result.stdout


@pytest.mark.integration
@pytest.mark.task
class TestUserExperience:
    """Test user experience aspects"""

    def test_help_output(self, runner):
        """Test help output is comprehensive"""
        result = runner.invoke(task_app, ["--help"])
        assert result.exit_code == 0
        assert "High-level DevSecOps task automation" in result.stdout

    def test_command_help(self, runner):
        """Test individual command help"""
        result = runner.invoke(task_app, ["security-audit", "--help"])
        assert result.exit_code == 0
        assert "Perform comprehensive security audit" in result.stdout

    def test_verbose_output(
        self,
        runner,
        mock_aws_session,
        mock_iam_client,
        mock_ec2_client,
        mock_s3_client,
        mock_secrets_client,
    ):
        """Test verbose output provides detailed information"""
        mock_aws_session.client.side_effect = [
            mock_iam_client,
            mock_ec2_client,
            mock_s3_client,
            mock_secrets_client,
        ]

        result = runner.invoke(task_app, ["security-audit", "--verbose"])
        assert result.exit_code == 0
        assert "Security audit completed" in result.stdout

    def test_output_formats(
        self,
        runner,
        mock_aws_session,
        mock_iam_client,
        mock_ec2_client,
        mock_s3_client,
        mock_secrets_client,
    ):
        """Test different output formats work correctly"""
        mock_aws_session.client.side_effect = [
            mock_iam_client,
            mock_ec2_client,
            mock_s3_client,
            mock_secrets_client,
        ]

        # Test JSON output
        result = runner.invoke(task_app, ["security-audit", "--output", "json"])
        assert result.exit_code == 0

        # Test CSV output
        result = runner.invoke(task_app, ["security-audit", "--output", "csv"])
        assert result.exit_code == 0


@pytest.mark.unit
@pytest.mark.task
class TestIntegration:
    """Test integration with other modules"""

    def test_task_module_import(self):
        """Test that task module can be imported correctly"""
        from src.awdx.task import task_app

        assert task_app is not None

    def test_cli_integration(self, runner):
        """Test that task commands are available in main CLI"""
        from src.awdx.cli import app

        result = runner.invoke(app, ["task", "--help"])
        assert result.exit_code == 0
        assert "High-level DevSecOps task automation" in result.stdout

    def test_ai_intents_integration(self):
        """Test that AI intents are properly defined"""
        from src.awdx.task.intents import TASK_INTENTS

        assert len(TASK_INTENTS) > 0
        assert all("intent" in intent for intent in TASK_INTENTS)
        assert all("examples" in intent for intent in TASK_INTENTS)
        assert all("command" in intent for intent in TASK_INTENTS)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
