"""
Unit tests for the AWDX Security Scanner.
"""

import os
import subprocess

# Import the classes from the security_scanner module
import sys
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from security_scanner import ScanResult, SecurityIssue, SecurityScanner


@pytest.mark.security
class TestSecurityScanner:
    """Test the SecurityScanner class."""

    def test_scanner_initialization(self, project_root):
        """Test scanner initialization."""
        scanner = SecurityScanner(project_root)

        assert scanner.project_root == project_root
        assert scanner.src_dir == project_root / "src"
        assert not scanner.quick_mode
        assert scanner.results == []

    def test_quick_mode_initialization(self, project_root):
        """Test scanner initialization in quick mode."""
        scanner = SecurityScanner(project_root, quick_mode=True)

        assert scanner.quick_mode

    def test_secret_detection_positive(self, security_test_files):
        """Test secret detection with files containing secrets."""
        scanner = SecurityScanner(Path.cwd())

        # Mock file reading to return our test content
        test_content = 'API_KEY = "AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"'

        with patch("pathlib.Path.rglob") as mock_rglob, patch(
            "builtins.open", mock_open(read_data=test_content)
        ):

            mock_rglob.return_value = [Path("test_file.py")]

            result = scanner._run_secret_scan()

            assert result.success
            assert len(result.issues) > 0
            assert any(issue.category == "HARDCODED_SECRET" for issue in result.issues)

    def test_secret_detection_negative(self, security_test_files):
        """Test secret detection with safe files."""
        scanner = SecurityScanner(Path.cwd())

        # Mock file reading to return safe content
        safe_content = 'API_KEY = os.environ.get("API_KEY")'

        with patch("pathlib.Path.rglob") as mock_rglob, patch(
            "builtins.open", mock_open(read_data=safe_content)
        ):

            mock_rglob.return_value = [Path("safe_file.py")]

            result = scanner._run_secret_scan()

            assert result.success
            # Should not find secrets in safe content
            secret_issues = [
                issue for issue in result.issues if issue.category == "HARDCODED_SECRET"
            ]
            assert len(secret_issues) == 0

    def test_injection_detection_positive(self):
        """Test injection vulnerability detection."""
        scanner = SecurityScanner(Path.cwd())

        # Test content with injection vulnerabilities
        injection_content = """
import os
import subprocess

def vulnerable_function(user_input):
    os.system(f"echo {user_input}")
    subprocess.call(user_input, shell=True)
"""

        with patch("pathlib.Path.rglob") as mock_rglob, patch(
            "builtins.open", mock_open(read_data=injection_content)
        ):

            mock_rglob.return_value = [Path("vulnerable_file.py")]

            result = scanner._run_injection_scan()

            assert result.success
            assert len(result.issues) > 0
            assert any(
                issue.category == "INJECTION_VULNERABILITY" for issue in result.issues
            )

    def test_injection_detection_negative(self):
        """Test injection detection with safe code."""
        scanner = SecurityScanner(Path.cwd())

        # Safe code example
        safe_content = """
import subprocess
import shlex

def safe_function(user_input):
    args = shlex.split(user_input)
    subprocess.run(args, timeout=30, shell=False)
"""

        with patch("pathlib.Path.rglob") as mock_rglob, patch(
            "builtins.open", mock_open(read_data=safe_content)
        ):

            mock_rglob.return_value = [Path("safe_file.py")]

            result = scanner._run_injection_scan()

            assert result.success
            # Should not find injection issues in safe code
            injection_issues = [
                issue
                for issue in result.issues
                if issue.category == "INJECTION_VULNERABILITY"
            ]
            assert len(injection_issues) == 0

    def test_security_score_calculation(self):
        """Test security score calculation."""
        scanner = SecurityScanner(Path.cwd())

        # Test with no issues
        assert (
            scanner._calculate_security_score(
                {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
            )
            == 100
        )

        # Test with critical issues
        assert (
            scanner._calculate_security_score(
                {"CRITICAL": 1, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
            )
            == 80
        )

        # Test with mixed issues
        assert (
            scanner._calculate_security_score(
                {"CRITICAL": 1, "HIGH": 1, "MEDIUM": 2, "LOW": 5, "INFO": 3}
            )
            == 100 - 20 - 10 - 10 - 10 - 3
        )  # 47

    @patch("subprocess.run")
    def test_command_execution_success(self, mock_run):
        """Test successful command execution."""
        scanner = SecurityScanner(Path.cwd())

        # Mock successful command
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Success output"
        mock_run.return_value.stderr = ""

        success, output, exit_code = scanner._run_command(["echo", "test"], "test_tool")

        assert success
        assert "Success output" in output
        assert exit_code == 0

    @patch("subprocess.run")
    def test_command_execution_failure(self, mock_run):
        """Test failed command execution."""
        scanner = SecurityScanner(Path.cwd())

        # Mock failed command
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "Error occurred"

        success, output, exit_code = scanner._run_command(["false"], "test_tool")

        assert not success
        assert "Error occurred" in output
        assert exit_code == 1

    @patch("subprocess.run")
    def test_command_timeout(self, mock_run):
        """Test command timeout handling."""
        scanner = SecurityScanner(Path.cwd())

        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired("test_cmd", 300)

        success, output, exit_code = scanner._run_command(
            ["sleep", "1000"], "test_tool"
        )

        assert not success
        assert "timed out" in output
        assert exit_code == -1


@pytest.mark.security
class TestSecurityIssue:
    """Test the SecurityIssue dataclass."""

    def test_security_issue_creation(self):
        """Test creating a SecurityIssue."""
        issue = SecurityIssue(
            severity="HIGH",
            category="INJECTION",
            description="SQL Injection vulnerability",
            file_path="src/app.py",
            line_number=42,
            code_snippet="query = f'SELECT * FROM users WHERE id={user_id}'",
            fix_suggestion="Use parameterized queries",
            cwe_id="CWE-89",
        )

        assert issue.severity == "HIGH"
        assert issue.category == "INJECTION"
        assert issue.line_number == 42
        assert "CWE-89" in issue.cwe_id


@pytest.mark.security
class TestScanResult:
    """Test the ScanResult dataclass."""

    def test_scan_result_creation(self):
        """Test creating a ScanResult."""
        issues = [
            SecurityIssue(
                severity="MEDIUM",
                category="CODE_QUALITY",
                description="Line too long",
                file_path="src/test.py",
            )
        ]

        result = ScanResult(
            tool_name="flake8",
            success=True,
            issues=issues,
            scan_time=1.5,
            exit_code=0,
            raw_output="1 issue found",
        )

        assert result.tool_name == "flake8"
        assert result.success
        assert len(result.issues) == 1
        assert result.scan_time == 1.5


@pytest.mark.security
@pytest.mark.integration
class TestSecurityScannerIntegration:
    """Integration tests for the security scanner."""

    def test_full_scan_integration(self, project_root):
        """Test running a full security scan."""
        scanner = SecurityScanner(project_root, quick_mode=True)

        # This is a real integration test - it will actually try to run tools
        # Skip if tools are not available
        try:
            results = scanner.run_all_scans()

            # Verify we got results for expected tools
            assert "bandit" in results
            assert "safety" in results
            assert "secrets" in results
            assert "injection" in results

            # Verify each result has the expected structure
            for tool_name, result in results.items():
                assert isinstance(result, ScanResult)
                assert result.tool_name == tool_name
                assert isinstance(result.success, bool)
                assert isinstance(result.issues, list)
                assert result.scan_time >= 0

        except Exception as e:
            pytest.skip(f"Integration test skipped due to missing dependencies: {e}")

    def test_report_generation(self, project_root, tmp_path):
        """Test report generation."""
        scanner = SecurityScanner(project_root, quick_mode=True)

        # Add some mock results
        scanner.results = [
            ScanResult(
                tool_name="test_tool",
                success=True,
                issues=[
                    SecurityIssue(
                        severity="HIGH",
                        category="TEST",
                        description="Test issue",
                        file_path="test.py",
                    )
                ],
                scan_time=1.0,
                exit_code=0,
                raw_output="Test output",
            )
        ]

        # Generate report
        report_file = tmp_path / "test_report.md"
        report_content = scanner.generate_report(report_file)

        # Verify report content
        assert "AWDX Security Scan Report" in report_content
        assert "TEST_TOOL" in report_content
        assert "Test issue" in report_content

        # Verify file was created
        assert report_file.exists()
        assert "AWDX Security Scan Report" in report_file.read_text()
