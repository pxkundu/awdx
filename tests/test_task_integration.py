"""
Integration tests for AWDX Task Module

Tests the task module integration with the main CLI and AI configuration.
"""

import os
import subprocess
import sys
import tempfile
from unittest.mock import Mock, patch

import pytest


@pytest.mark.integration
@pytest.mark.task
def test_task_module_help():
    """Test that task module help works correctly"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "--help"], capture_output=True, text=True
    )

    assert result.returncode == 0
    assert "High-level DevSecOps task automation" in result.stdout
    assert "security-audit" in result.stdout
    assert "cost-optimize" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_task_help_command():
    """Test the detailed help command"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "help"], capture_output=True, text=True
    )

    assert result.returncode == 0
    assert "AWDX Task Module" in result.stdout
    assert "AI Integration" in result.stdout
    assert "Available Commands" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_security_audit_help():
    """Test security audit help"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "security-audit", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "comprehensive security audit" in result.stdout
    assert "--comprehensive" in result.stdout
    assert "--fix-safe" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_cost_optimize_help():
    """Test cost optimize help"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "cost-optimize", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "optimize AWS costs" in result.stdout
    assert "--auto-fix" in result.stdout
    assert "--dry-run" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_compliance_check_help():
    """Test compliance check help"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "compliance-check", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "compliance checks" in result.stdout
    assert "--framework" in result.stdout
    assert "--quick" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_security_monitor_help():
    """Test security monitor help"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "security-monitor", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "security monitoring" in result.stdout
    assert "--continuous" in result.stdout
    assert "--alert" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_secret_rotate_help():
    """Test secret rotate help"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "secret-rotate", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "secret rotation" in result.stdout
    assert "--auto" in result.stdout
    assert "--schedule" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_vuln_scan_help():
    """Test vulnerability scan help"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "vuln-scan", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "vulnerability scanning" in result.stdout
    assert "--auto-remediate" in result.stdout
    assert "--low-risk" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_task_module_without_aws_credentials():
    """Test task module gracefully handles missing AWS credentials"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "security-audit"],
        capture_output=True,
        text=True,
    )

    # Should fail gracefully with clear error message
    assert result.returncode == 1
    assert "Security audit failed" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_task_module_invalid_command():
    """Test task module handles invalid commands gracefully"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "invalid-command"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2  # Typer error code for invalid command
    assert "No such command" in result.stderr


@pytest.mark.integration
@pytest.mark.task
def test_task_module_with_verbose():
    """Test task module with verbose flag"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "security-audit", "--verbose"],
        capture_output=True,
        text=True,
    )

    # Should fail due to AWS credentials, but verbose flag should be accepted
    assert result.returncode == 1
    assert "Security audit failed" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_task_module_with_region():
    """Test task module with region parameter"""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "awdx",
            "task",
            "security-audit",
            "--region",
            "us-east-1",
        ],
        capture_output=True,
        text=True,
    )

    # Should fail due to AWS credentials, but region parameter should be accepted
    assert result.returncode == 1
    assert "Security audit failed" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_task_module_output_formats():
    """Test task module accepts different output formats"""
    formats = ["table", "json", "csv"]

    for output_format in formats:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "awdx",
                "task",
                "security-audit",
                "--output",
                output_format,
            ],
            capture_output=True,
            text=True,
        )

        # Should fail due to AWS credentials, but output format should be accepted
        assert result.returncode == 1
        assert "Security audit failed" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_task_module_comprehensive_flag():
    """Test task module with comprehensive flag"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "security-audit", "--comprehensive"],
        capture_output=True,
        text=True,
    )

    # Should fail due to AWS credentials, but comprehensive flag should be accepted
    assert result.returncode == 1
    assert "Security audit failed" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_task_module_fix_safe_flag():
    """Test task module with fix-safe flag"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "security-audit", "--fix-safe"],
        capture_output=True,
        text=True,
    )

    # Should fail due to AWS credentials, but fix-safe flag should be accepted
    assert result.returncode == 1
    assert "Security audit failed" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_cost_optimize_dry_run():
    """Test cost optimize with dry-run flag"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "cost-optimize", "--dry-run"],
        capture_output=True,
        text=True,
    )

    # Should fail due to AWS credentials, but dry-run flag should be accepted
    assert result.returncode == 1
    assert "Cost optimization failed" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_cost_optimize_auto_fix():
    """Test cost optimize with auto-fix flag"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "cost-optimize", "--auto-fix"],
        capture_output=True,
        text=True,
    )

    # Should fail due to AWS credentials, but auto-fix flag should be accepted
    assert result.returncode == 1
    assert "Cost optimization failed" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_compliance_check_frameworks():
    """Test compliance check with different frameworks"""
    frameworks = ["sox", "hipaa", "pci-dss", "soc2", "iso27001", "nist", "all"]

    for framework in frameworks:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "awdx",
                "task",
                "compliance-check",
                "--framework",
                framework,
            ],
            capture_output=True,
            text=True,
        )

        # Should fail due to AWS credentials, but framework should be accepted
        assert result.returncode == 1
        assert "Compliance check failed" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_security_monitor_continuous():
    """Test security monitor with continuous flag"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "security-monitor", "--continuous"],
        capture_output=True,
        text=True,
    )

    # Should fail due to AWS credentials, but continuous flag should be accepted
    assert result.returncode == 1
    assert "Security monitoring failed" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_secret_rotate_auto():
    """Test secret rotate with auto flag"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "secret-rotate", "--auto"],
        capture_output=True,
        text=True,
    )

    # Should fail due to AWS credentials, but auto flag should be accepted
    assert result.returncode == 1
    assert "Secret rotation failed" in result.stdout


@pytest.mark.integration
@pytest.mark.task
def test_vuln_scan_auto_remediate():
    """Test vulnerability scan with auto-remediate flag"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "task", "vuln-scan", "--auto-remediate"],
        capture_output=True,
        text=True,
    )

    # Should fail due to AWS credentials, but auto-remediate flag should be accepted
    assert result.returncode == 1
    assert "Vulnerability scan failed" in result.stdout


@pytest.mark.unit
@pytest.mark.task
def test_task_module_import():
    """Test that task module can be imported correctly"""
    try:
        from src.awdx.task import task_app

        assert task_app is not None
    except ImportError as e:
        pytest.fail(f"Failed to import task module: {e}")


@pytest.mark.unit
@pytest.mark.task
def test_task_intents_import():
    """Test that task intents can be imported correctly"""
    try:
        from src.awdx.task.intents import TASK_INTENTS

        assert len(TASK_INTENTS) > 0
        assert all("intent" in intent for intent in TASK_INTENTS)
        assert all("examples" in intent for intent in TASK_INTENTS)
        assert all("command" in intent for intent in TASK_INTENTS)
    except ImportError as e:
        pytest.fail(f"Failed to import task intents: {e}")


@pytest.mark.unit
@pytest.mark.task
def test_cli_integration():
    """Test that task module is properly integrated with main CLI"""
    result = subprocess.run(
        [sys.executable, "-m", "awdx", "--help"], capture_output=True, text=True
    )

    assert result.returncode == 0
    assert "task" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
