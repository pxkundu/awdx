#!/usr/bin/env python3
"""
🔒 AWDX Security Scanner
========================

Comprehensive automated security testing suite for AWDX.
Performs the same security checks as our manual audit.

Usage:
    python tests/security_scanner.py [--quick] [--report] [--fix]
    
Options:
    --quick     Run only critical security checks (faster)
    --report    Generate detailed HTML report
    --fix       Automatically fix certain issues (formatting, imports)
    --help      Show this help message

Requirements:
    pip install -e ".[test]"
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    from rich.markdown import Markdown
except ImportError:
    print("❌ Missing dependencies. Install with: pip install -e '.[test]'")
    sys.exit(1)

console = Console()

@dataclass
class SecurityIssue:
    """Represents a security issue found during scanning."""
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"
    category: str  # "INJECTION", "SECRETS", "DEPENDENCIES", etc.
    description: str
    file_path: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    fix_suggestion: Optional[str] = None
    cwe_id: Optional[str] = None

@dataclass
class ScanResult:
    """Results from a security scan."""
    tool_name: str
    success: bool
    issues: List[SecurityIssue]
    scan_time: float
    exit_code: int
    raw_output: str
    error_message: Optional[str] = None

class SecurityScanner:
    """Main security scanner class."""
    
    def __init__(self, project_root: Path, quick_mode: bool = False):
        self.project_root = project_root
        self.quick_mode = quick_mode
        self.src_dir = project_root / "src"
        self.results: List[ScanResult] = []
        self.start_time = time.time()
        
    def run_all_scans(self) -> Dict[str, ScanResult]:
        """Run all security scans and return results."""
        # Import version dynamically
        try:
            from awdx import __version__
            version_str = __version__
        except ImportError:
            version_str = "0.0.9-dev"
        
        console.print(f"🔒 [bold blue]AWDX Security Scanner v{version_str}[/bold blue]")
        console.print(f"📁 Scanning project: {self.project_root}")
        console.print(f"⚡ Mode: {'Quick' if self.quick_mode else 'Comprehensive'}")
        console.print()
        
        scans = [
            ("bandit", "🛡️  Security Vulnerabilities", self._run_bandit_scan),
            ("safety", "📦 Dependency Vulnerabilities", self._run_safety_scan),
            ("secrets", "🔑 Secret Detection", self._run_secret_scan),
            ("injection", "💉 Injection Patterns", self._run_injection_scan),
        ]
        
        if not self.quick_mode:
            scans.extend([
                ("flake8", "📝 Code Quality", self._run_flake8_scan),
                ("mypy", "🎯 Type Safety", self._run_mypy_scan),
                ("custom", "🔍 Custom Security Checks", self._run_custom_security_checks),
            ])
        
        results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            for scan_id, description, scan_func in scans:
                task = progress.add_task(description, total=1)
                try:
                    result = scan_func()
                    results[scan_id] = result
                    self.results.append(result)
                    
                    # Show immediate results
                    if result.success:
                        issue_count = len(result.issues)
                        if issue_count == 0:
                            console.print(f"✅ {description}: [green]No issues found[/green]")
                        else:
                            severity_counts = {}
                            for issue in result.issues:
                                severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
                            
                            status_parts = []
                            for severity, count in severity_counts.items():
                                color = {
                                    "CRITICAL": "red",
                                    "HIGH": "red", 
                                    "MEDIUM": "yellow",
                                    "LOW": "blue",
                                    "INFO": "dim"
                                }.get(severity, "white")
                                status_parts.append(f"[{color}]{count} {severity}[/{color}]")
                            
                            status = " | ".join(status_parts)
                            console.print(f"⚠️  {description}: {status}")
                    else:
                        console.print(f"❌ {description}: [red]Scan failed[/red]")
                        if result.error_message:
                            console.print(f"   Error: {result.error_message}")
                            
                except Exception as e:
                    console.print(f"❌ {description}: [red]Exception: {e}[/red]")
                    results[scan_id] = ScanResult(
                        tool_name=scan_id,
                        success=False,
                        issues=[],
                        scan_time=0.0,
                        exit_code=-1,
                        raw_output="",
                        error_message=str(e)
                    )
                
                progress.update(task, completed=1)
        
        return results
    
    def _run_command(self, cmd: List[str], tool_name: str) -> Tuple[bool, str, int]:
        """Run a command and return success, output, exit_code."""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode == 0, result.stdout + result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return False, f"{tool_name} timed out after 5 minutes", -1
        except FileNotFoundError:
            return False, f"{tool_name} not found. Install with: pip install {tool_name}", -1
        except Exception as e:
            return False, f"Error running {tool_name}: {e}", -1
    
    def _run_bandit_scan(self) -> ScanResult:
        """Run Bandit security vulnerability scan."""
        start_time = time.time()
        
        # Create temporary file for JSON output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_file = f.name
        
        try:
            cmd = [
                "bandit", "-r", "src/", 
                "-f", "json", 
                "-o", json_file,
                "--severity-level", "medium"
            ]
            
            success, output, exit_code = self._run_command(cmd, "bandit")
            scan_time = time.time() - start_time
            
            issues = []
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r') as f:
                        bandit_data = json.load(f)
                    
                    for result in bandit_data.get('results', []):
                        severity_map = {
                            "HIGH": "HIGH",
                            "MEDIUM": "MEDIUM", 
                            "LOW": "LOW"
                        }
                        
                        issues.append(SecurityIssue(
                            severity=severity_map.get(result.get('issue_severity', 'LOW'), 'LOW'),
                            category="SECURITY_VULNERABILITY",
                            description=result.get('issue_text', 'Unknown issue'),
                            file_path=result.get('filename', ''),
                            line_number=result.get('line_number'),
                            code_snippet=result.get('code', ''),
                            fix_suggestion=f"See: {result.get('more_info', '')}",
                            cwe_id=result.get('issue_cwe', {}).get('id')
                        ))
                        
                except json.JSONDecodeError:
                    pass
            
            return ScanResult(
                tool_name="bandit",
                success=success,
                issues=issues,
                scan_time=scan_time,
                exit_code=exit_code,
                raw_output=output
            )
            
        finally:
            if os.path.exists(json_file):
                os.unlink(json_file)
    
    def _run_safety_scan(self) -> ScanResult:
        """Run Safety dependency vulnerability scan."""
        start_time = time.time()
        
        cmd = ["safety", "scan", "--json"]
        success, output, exit_code = self._run_command(cmd, "safety")
        scan_time = time.time() - start_time
        
        issues = []
        try:
            if output and output.strip().startswith('{'):
                safety_data = json.loads(output)
                vulnerabilities = safety_data.get('vulnerabilities', [])
                
                for vuln in vulnerabilities:
                    issues.append(SecurityIssue(
                        severity="HIGH",
                        category="DEPENDENCY_VULNERABILITY",
                        description=f"Vulnerable dependency: {vuln.get('package_name')} {vuln.get('analyzed_version')}",
                        file_path="requirements/dependencies",
                        fix_suggestion=f"Update to version {vuln.get('more_info_url', 'latest')}"
                    ))
        except json.JSONDecodeError:
            # Safety scan successful but no JSON output means no vulnerabilities
            pass
        
        return ScanResult(
            tool_name="safety",
            success=success,
            issues=issues,
            scan_time=scan_time,
            exit_code=exit_code,
            raw_output=output
        )
    
    def _run_secret_scan(self) -> ScanResult:
        """Run custom secret detection scan."""
        start_time = time.time()
        
        secret_patterns = [
            (r'AIza[0-9A-Za-z_-]{35}', 'Google API Key'),
            (r'sk-[a-zA-Z0-9]{20,50}', 'OpenAI API Key'),
            (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
            (r'xoxb-[0-9]{11,12}-[0-9]{12}-[0-9A-Za-z]{24}', 'Slack Bot Token'),
            (r'ghp_[0-9A-Za-z]{36}', 'GitHub Personal Access Token'),
            (r'(?i)password\s*[=:]\s*["\'][^"\']{8,}["\']', 'Hardcoded Password'),
            (r'(?i)secret\s*[=:]\s*["\'][^"\']{8,}["\']', 'Hardcoded Secret'),
            (r'(?i)token\s*[=:]\s*["\'][^"\']{20,}["\']', 'Hardcoded Token'),
        ]
        
        issues = []
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern, secret_type in secret_patterns:
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            # Skip test files and comments
                            if ('test' in str(py_file).lower() or 
                                line.strip().startswith('#') or
                                'placeholder' in line.lower() or
                                'example' in line.lower()):
                                continue
                                
                            issues.append(SecurityIssue(
                                severity="HIGH",
                                category="HARDCODED_SECRET",
                                description=f"Potential {secret_type} found",
                                file_path=str(py_file.relative_to(self.project_root)),
                                line_number=line_num,
                                code_snippet=line.strip(),
                                fix_suggestion="Move to environment variables or secure configuration"
                            ))
                            
            except (UnicodeDecodeError, PermissionError):
                continue
        
        scan_time = time.time() - start_time
        
        return ScanResult(
            tool_name="secret_scanner",
            success=True,
            issues=issues,
            scan_time=scan_time,
            exit_code=0,
            raw_output=f"Scanned {len(list(self.src_dir.rglob('*.py')))} Python files"
        )
    
    def _run_injection_scan(self) -> ScanResult:
        """Scan for injection vulnerabilities."""
        start_time = time.time()
        
        injection_patterns = [
            (r'os\.system\s*\(', 'OS Command Injection', 'Use subprocess with shell=False'),
            (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', 'Shell Injection', 'Use shell=False'),
            (r'eval\s*\(', 'Code Injection', 'Avoid eval(), use ast.literal_eval()'),
            (r'exec\s*\(', 'Code Injection', 'Avoid exec(), use safer alternatives'),
            (r'\.format\s*\(\s*\*', 'Format String Injection', 'Use f-strings or % formatting'),
            (r'sql.*[\'"].*\+.*[\'"]', 'SQL Injection', 'Use parameterized queries'),
        ]
        
        issues = []
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern, vuln_type, fix_suggestion in injection_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Skip if it's in a comment or test file
                            if (line.strip().startswith('#') or 
                                'test' in str(py_file).lower()):
                                continue
                                
                            issues.append(SecurityIssue(
                                severity="HIGH",
                                category="INJECTION_VULNERABILITY",
                                description=f"Potential {vuln_type}",
                                file_path=str(py_file.relative_to(self.project_root)),
                                line_number=line_num,
                                code_snippet=line.strip(),
                                fix_suggestion=fix_suggestion
                            ))
                            
            except (UnicodeDecodeError, PermissionError):
                continue
        
        scan_time = time.time() - start_time
        
        return ScanResult(
            tool_name="injection_scanner",
            success=True,
            issues=issues,
            scan_time=scan_time,
            exit_code=0,
            raw_output=f"Scanned {len(list(self.src_dir.rglob('*.py')))} Python files for injection patterns"
        )
    
    def _run_flake8_scan(self) -> ScanResult:
        """Run Flake8 code quality scan."""
        start_time = time.time()
        
        cmd = [
            "flake8", "src/", 
            "--max-line-length=120",
            "--ignore=E203,W503",
            "--statistics"
        ]
        
        success, output, exit_code = self._run_command(cmd, "flake8")
        scan_time = time.time() - start_time
        
        issues = []
        for line in output.split('\n'):
            if ':' in line and ('E' in line or 'W' in line or 'F' in line):
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    file_path = parts[0]
                    line_num = parts[1]
                    error_code = parts[3].strip().split()[0] if parts[3].strip() else 'Unknown'
                    description = parts[3].strip()
                    
                    severity = "LOW"
                    if error_code.startswith('F'):  # Pyflakes errors
                        severity = "MEDIUM"
                    elif error_code.startswith('E9') or error_code.startswith('W6'):
                        severity = "MEDIUM"
                    
                    issues.append(SecurityIssue(
                        severity=severity,
                        category="CODE_QUALITY",
                        description=description,
                        file_path=file_path,
                        line_number=int(line_num) if line_num.isdigit() else None,
                        fix_suggestion="See flake8 documentation for this error code"
                    ))
        
        return ScanResult(
            tool_name="flake8",
            success=success,
            issues=issues,
            scan_time=scan_time,
            exit_code=exit_code,
            raw_output=output
        )
    
    def _run_mypy_scan(self) -> ScanResult:
        """Run MyPy type checking scan."""
        start_time = time.time()
        
        cmd = ["mypy", "src/", "--ignore-missing-imports"]
        success, output, exit_code = self._run_command(cmd, "mypy")
        scan_time = time.time() - start_time
        
        issues = []
        for line in output.split('\n'):
            if ':' in line and 'error:' in line:
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    file_path = parts[0]
                    line_num = parts[1]
                    description = parts[3].strip() if 'error:' in parts[3] else line
                    
                    issues.append(SecurityIssue(
                        severity="LOW",
                        category="TYPE_SAFETY",
                        description=description,
                        file_path=file_path,
                        line_number=int(line_num) if line_num.isdigit() else None,
                        fix_suggestion="Add proper type hints"
                    ))
        
        return ScanResult(
            tool_name="mypy",
            success=True,  # MyPy errors are warnings, not failures
            issues=issues,
            scan_time=scan_time,
            exit_code=exit_code,
            raw_output=output
        )
    
    def _run_custom_security_checks(self) -> ScanResult:
        """Run custom AWDX-specific security checks."""
        start_time = time.time()
        issues = []
        
        # Check for proper AI engine security
        ai_engine_files = list((self.src_dir / "awdx" / "ai_engine").glob("*.py"))
        for py_file in ai_engine_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for proper command validation
                if "subprocess.run" in content and "shlex.split" not in content:
                    issues.append(SecurityIssue(
                        severity="MEDIUM",
                        category="COMMAND_INJECTION",
                        description="subprocess.run without shlex.split() validation",
                        file_path=str(py_file.relative_to(self.project_root)),
                        fix_suggestion="Use shlex.split() for command parsing"
                    ))
                
                # Check for proper timeout handling
                if "subprocess.run" in content and "timeout=" not in content:
                    issues.append(SecurityIssue(
                        severity="LOW",
                        category="RESOURCE_EXHAUSTION",
                        description="subprocess.run without timeout protection",
                        file_path=str(py_file.relative_to(self.project_root)),
                        fix_suggestion="Add timeout parameter to subprocess.run()"
                    ))
                
            except (UnicodeDecodeError, PermissionError):
                continue
        
        # Check configuration files for sensitive data
        config_files = list(self.project_root.glob("*.toml")) + list(self.project_root.glob("*.yaml")) + list(self.project_root.glob("*.yml"))
        for config_file in config_files:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if re.search(r'(password|secret|key)\s*=\s*[\'"][^\'"]{10,}[\'"]', content, re.IGNORECASE):
                    issues.append(SecurityIssue(
                        severity="HIGH",
                        category="CONFIGURATION_SECRET",
                        description="Potential secret in configuration file",
                        file_path=str(config_file.relative_to(self.project_root)),
                        fix_suggestion="Use environment variables for secrets"
                    ))
            except (UnicodeDecodeError, PermissionError):
                continue
        
        scan_time = time.time() - start_time
        
        return ScanResult(
            tool_name="custom_security",
            success=True,
            issues=issues,
            scan_time=scan_time,
            exit_code=0,
            raw_output=f"Ran {len(issues)} custom security checks"
        )
    
    def generate_report(self, output_file: Optional[Path] = None) -> str:
        """Generate comprehensive security report."""
        total_time = time.time() - self.start_time
        
        # Count issues by severity
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        all_issues = []
        
        for result in self.results:
            for issue in result.issues:
                severity_counts[issue.severity] += 1
                all_issues.append(issue)
        
        # Generate report
        report = f"""# 🔒 AWDX Security Scan Report
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Scan Mode**: {'Quick' if self.quick_mode else 'Comprehensive'}  
**Total Scan Time**: {total_time:.2f} seconds  
**AWDX Version**: 0.0.8

## 📊 Executive Summary

**Security Score**: {self._calculate_security_score(severity_counts)}/100

| Severity | Count |
|----------|-------|
| 🔴 Critical | {severity_counts['CRITICAL']} |
| 🟠 High | {severity_counts['HIGH']} |
| 🟡 Medium | {severity_counts['MEDIUM']} |
| 🔵 Low | {severity_counts['LOW']} |
| ℹ️  Info | {severity_counts['INFO']} |

## 🛠️ Scan Results

"""
        
        for result in self.results:
            status = "✅ PASSED" if result.success and len(result.issues) == 0 else "⚠️ ISSUES FOUND" if result.success else "❌ FAILED"
            report += f"### {result.tool_name.upper()} - {status}\n"
            report += f"**Scan time**: {result.scan_time:.2f}s  \n"
            report += f"**Issues found**: {len(result.issues)}  \n"
            
            if result.issues:
                report += "\n**Issues:**\n"
                for issue in result.issues[:10]:  # Limit to top 10 issues per tool
                    report += f"- **{issue.severity}**: {issue.description}\n"
                    if issue.file_path:
                        report += f"  - File: `{issue.file_path}`"
                        if issue.line_number:
                            report += f":{issue.line_number}"
                        report += "\n"
                    if issue.fix_suggestion:
                        report += f"  - Fix: {issue.fix_suggestion}\n"
                if len(result.issues) > 10:
                    report += f"  - ... and {len(result.issues) - 10} more issues\n"
            
            report += "\n"
        
        # Critical issues section
        critical_issues = [issue for issue in all_issues if issue.severity in ["CRITICAL", "HIGH"]]
        if critical_issues:
            report += "## 🚨 Critical Issues Requiring Immediate Attention\n\n"
            for issue in critical_issues:
                report += f"### {issue.severity}: {issue.description}\n"
                report += f"**File**: `{issue.file_path}`"
                if issue.line_number:
                    report += f":{issue.line_number}"
                report += "\n"
                if issue.code_snippet:
                    report += f"```python\n{issue.code_snippet}\n```\n"
                if issue.fix_suggestion:
                    report += f"**Fix**: {issue.fix_suggestion}\n"
                report += "\n"
        
        # Recommendations
        report += "## 🚀 Recommendations\n\n"
        if severity_counts['CRITICAL'] > 0:
            report += "- 🚨 **URGENT**: Fix critical security vulnerabilities before deployment\n"
        if severity_counts['HIGH'] > 0:
            report += "- ⚠️ **HIGH PRIORITY**: Address high severity issues\n"
        if severity_counts['MEDIUM'] > 0:
            report += "- 📋 **MEDIUM PRIORITY**: Review and fix medium severity issues\n"
        if sum(severity_counts.values()) == 0:
            report += "- ✅ **All clear**: No security issues found!\n"
        
        # Use dynamic version in report
        try:
            from awdx import __version__
            version_str = __version__
        except ImportError:
            version_str = "0.0.9-dev"
        
        report += f"\n---\n*Generated by AWDX Security Scanner v{version_str}*"
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            console.print(f"📄 Report saved to: {output_file}")
        
        return report
    
    def _calculate_security_score(self, severity_counts: Dict[str, int]) -> int:
        """Calculate security score based on issue severity."""
        score = 100
        score -= severity_counts['CRITICAL'] * 20
        score -= severity_counts['HIGH'] * 10
        score -= severity_counts['MEDIUM'] * 5
        score -= severity_counts['LOW'] * 2
        score -= severity_counts['INFO'] * 1
        return max(0, score)
    
    def display_summary(self):
        """Display a summary table of scan results."""
        table = Table(title="🔒 AWDX Security Scan Summary")
        table.add_column("Tool", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Issues", justify="right")
        table.add_column("Time", justify="right", style="dim")
        
        for result in self.results:
            status = "✅ PASSED" if result.success and len(result.issues) == 0 else "⚠️ ISSUES" if result.success else "❌ FAILED"
            issue_count = str(len(result.issues)) if result.success else "N/A"
            scan_time = f"{result.scan_time:.2f}s"
            
            table.add_row(
                result.tool_name.upper(),
                status,
                issue_count,
                scan_time
            )
        
        console.print(table)
        
        # Overall status
        total_issues = sum(len(result.issues) for result in self.results)
        critical_issues = sum(1 for result in self.results for issue in result.issues if issue.severity in ["CRITICAL", "HIGH"])
        
        if critical_issues > 0:
            console.print(f"\n🚨 [bold red]CRITICAL: {critical_issues} high/critical issues found![/bold red]")
            console.print("❌ [red]Not ready for production deployment[/red]")
        elif total_issues > 0:
            console.print(f"\n⚠️  [yellow]{total_issues} issues found (low/medium severity)[/yellow]")
            console.print("✅ [green]Ready for production with recommendations[/green]")
        else:
            console.print("\n🎉 [bold green]All security scans passed![/bold green]")
            console.print("✅ [green]Ready for production deployment[/green]")

def main():
    """Main entry point for the security scanner."""
    parser = argparse.ArgumentParser(description="AWDX Security Scanner")
    parser.add_argument("--quick", action="store_true", help="Run only critical security checks")
    parser.add_argument("--report", type=str, help="Generate detailed report to file")
    parser.add_argument("--fix", action="store_true", help="Automatically fix certain issues")
    
    args = parser.parse_args()
    
    # Find project root
    current_dir = Path.cwd()
    project_root = current_dir
    
    # Look for pyproject.toml to find project root
    while project_root.parent != project_root:
        if (project_root / "pyproject.toml").exists():
            break
        project_root = project_root.parent
    
    if not (project_root / "pyproject.toml").exists():
        console.print("❌ Could not find project root (no pyproject.toml found)")
        sys.exit(1)
    
    # Initialize scanner
    scanner = SecurityScanner(project_root, quick_mode=args.quick)
    
    # Run scans
    try:
        results = scanner.run_all_scans()
        
        # Display summary
        console.print()
        scanner.display_summary()
        
        # Generate report if requested
        if args.report:
            report_file = Path(args.report)
            scanner.generate_report(report_file)
        
        # Auto-fix if requested
        if args.fix:
            console.print("\n🔧 [yellow]Auto-fix functionality not yet implemented[/yellow]")
            console.print("   Suggested fixes are provided in the scan results")
        
        # Exit with appropriate code
        critical_issues = sum(1 for result in results.values() for issue in result.issues 
                            if issue.severity in ["CRITICAL", "HIGH"])
        
        if critical_issues > 0:
            sys.exit(1)  # Critical issues found
        else:
            sys.exit(0)  # All good
            
    except KeyboardInterrupt:
        console.print("\n🛑 [yellow]Scan interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n❌ [red]Unexpected error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main() 