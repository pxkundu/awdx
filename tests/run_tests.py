#!/usr/bin/env python3
"""
🧪 AWDX Test Runner
===================

Comprehensive test runner that combines security scanning and unit testing.

Usage:
    python tests/run_tests.py [--security] [--unit] [--integration] [--all] [--quick] [--coverage] [--report]

Options:
    --security      Run security tests only
    --unit          Run unit tests only
    --integration   Run integration tests only  
    --all           Run all tests (default)
    --quick         Quick security scan mode
    --coverage      Generate coverage report
    --report        Generate detailed reports
    --help          Show this help message

Examples:
    python tests/run_tests.py --all --coverage
    python tests/run_tests.py --security --quick
    python tests/run_tests.py --unit --coverage --report
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.markdown import Markdown
except ImportError:
    print("❌ Missing dependencies. Install with: pip install -e '.[test]'")
    sys.exit(1)

console = Console()

class TestRunner:
    """Main test runner class."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results = {}
        self.start_time = time.time()
    
    def run_security_tests(self, quick_mode: bool = False, generate_report: bool = False) -> bool:
        """Run security scanning tests."""
        console.print("🔒 [bold blue]Running Security Tests[/bold blue]")
        
        # Run security scanner
        security_script = self.project_root / "tests" / "security_scanner.py"
        if not security_script.exists():
            console.print("❌ Security scanner not found!")
            return False
        
        cmd = [sys.executable, str(security_script)]
        if quick_mode:
            cmd.append("--quick")
        if generate_report:
            cmd.extend(["--report", "security_report.md"])
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            self.results['security'] = {
                'success': result.returncode == 0,
                'output': result.stdout + result.stderr,
                'exit_code': result.returncode
            }
            
            if result.returncode == 0:
                console.print("✅ [green]Security tests passed[/green]")
            else:
                console.print("❌ [red]Security tests failed[/red]")
                console.print(result.stdout)
                console.print(result.stderr)
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            console.print("❌ [red]Security tests timed out[/red]")
            return False
        except Exception as e:
            console.print(f"❌ [red]Error running security tests: {e}[/red]")
            return False
    
    def run_unit_tests(self, coverage: bool = False) -> bool:
        """Run unit tests with pytest."""
        console.print("🧪 [bold blue]Running Unit Tests[/bold blue]")
        
        cmd = [sys.executable, "-m", "pytest"]
        
        # Test configuration
        cmd.extend([
            "tests/",
            "-v",
            "--tb=short",
            "-m", "unit",
            "--strict-markers"
        ])
        
        if coverage:
            cmd.extend([
                "--cov=src",
                "--cov-report=term-missing",
                "--cov-report=html:coverage_html",
                "--cov-report=xml:coverage.xml"
            ])
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            self.results['unit'] = {
                'success': result.returncode == 0,
                'output': result.stdout + result.stderr,
                'exit_code': result.returncode
            }
            
            console.print(result.stdout)
            if result.stderr:
                console.print(result.stderr)
            
            if result.returncode == 0:
                console.print("✅ [green]Unit tests passed[/green]")
            else:
                console.print("❌ [red]Unit tests failed[/red]")
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            console.print("❌ [red]Unit tests timed out[/red]")
            return False
        except Exception as e:
            console.print(f"❌ [red]Error running unit tests: {e}[/red]")
            return False
    
    def run_integration_tests(self) -> bool:
        """Run integration tests."""
        console.print("🔗 [bold blue]Running Integration Tests[/bold blue]")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short", 
            "-m", "integration",
            "--strict-markers"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            self.results['integration'] = {
                'success': result.returncode == 0,
                'output': result.stdout + result.stderr,
                'exit_code': result.returncode
            }
            
            console.print(result.stdout)
            if result.stderr:
                console.print(result.stderr)
            
            if result.returncode == 0:
                console.print("✅ [green]Integration tests passed[/green]")
            else:
                console.print("❌ [red]Integration tests failed[/red]")
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            console.print("❌ [red]Integration tests timed out[/red]")
            return False
        except Exception as e:
            console.print(f"❌ [red]Error running integration tests: {e}[/red]")
            return False
    
    def run_code_quality_checks(self) -> bool:
        """Run additional code quality checks."""
        console.print("📝 [bold blue]Running Code Quality Checks[/bold blue]")
        
        checks = [
            ("black --check --diff src/", "Code formatting (Black)"),
            ("isort --check-only --diff src/", "Import sorting (isort)"),
            ("mypy src/ --ignore-missing-imports", "Type checking (MyPy)")
        ]
        
        all_passed = True
        
        for cmd_str, description in checks:
            console.print(f"  Running: {description}")
            
            try:
                result = subprocess.run(
                    cmd_str.split(),
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    console.print(f"    ✅ [green]{description} passed[/green]")
                else:
                    console.print(f"    ❌ [red]{description} failed[/red]")
                    if result.stdout:
                        console.print(f"      Output: {result.stdout[:200]}...")
                    all_passed = False
                    
            except Exception as e:
                console.print(f"    ❌ [red]Error running {description}: {e}[/red]")
                all_passed = False
        
        self.results['code_quality'] = {
            'success': all_passed,
            'output': f"Code quality checks: {'passed' if all_passed else 'failed'}",
            'exit_code': 0 if all_passed else 1
        }
        
        return all_passed
    
    def install_dependencies(self) -> bool:
        """Install test dependencies."""
        console.print("📦 [bold blue]Installing Test Dependencies[/bold blue]")
        
        cmd = [sys.executable, "-m", "pip", "install", "-e", ".[test]"]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                console.print("✅ [green]Dependencies installed successfully[/green]")
                return True
            else:
                console.print("❌ [red]Failed to install dependencies[/red]")
                console.print(result.stderr)
                return False
                
        except Exception as e:
            console.print(f"❌ [red]Error installing dependencies: {e}[/red]")
            return False
    
    def generate_summary_report(self, output_file: Optional[Path] = None) -> str:
        """Generate a comprehensive test summary report."""
        total_time = time.time() - self.start_time
        
        # Count passed/failed tests
        passed_count = sum(1 for result in self.results.values() if result['success'])
        total_count = len(self.results)
        
        # Generate report
        report = f"""# 🧪 AWDX Test Summary Report
**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Total Runtime**: {total_time:.2f} seconds  
**Tests Passed**: {passed_count}/{total_count}  
**Success Rate**: {(passed_count/total_count*100):.1f}% 

## 📊 Test Results

| Test Suite | Status | Exit Code |
|------------|--------|-----------|
"""
        
        for test_name, result in self.results.items():
            status = "✅ PASSED" if result['success'] else "❌ FAILED"
            report += f"| {test_name.title()} | {status} | {result['exit_code']} |\n"
        
        report += "\n## 📋 Detailed Results\n\n"
        
        for test_name, result in self.results.items():
            report += f"### {test_name.title()} Tests\n"
            report += f"**Status**: {'✅ PASSED' if result['success'] else '❌ FAILED'}  \n"
            report += f"**Exit Code**: {result['exit_code']}  \n"
            
            if result['output']:
                # Truncate long outputs
                output = result['output']
                if len(output) > 1000:
                    output = output[:1000] + "\\n... (truncated)"
                report += f"**Output**:\n```\n{output}\n```\n"
            
            report += "\n"
        
        # Overall assessment
        if passed_count == total_count:
            report += "## 🎉 Overall Assessment\n\n✅ **All tests passed!** The codebase is ready for production.\n"
        elif passed_count >= total_count * 0.8:
            report += "## ⚠️ Overall Assessment\n\n⚠️ **Most tests passed** but some issues need attention before production.\n"
        else:
            report += "## ❌ Overall Assessment\n\n❌ **Multiple test failures** - significant issues need to be resolved.\n"
        
        # Use dynamic version in report
        try:
            from awdx import __version__
            version_str = __version__
        except ImportError:
            version_str = "0.1.0-dev"
        
        report += f"\n---\n*Generated by AWDX Test Runner v{version_str}*"
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            console.print(f"📄 Test report saved to: {output_file}")
        
        return report
    
    def display_summary(self):
        """Display test results summary table."""
        table = Table(title="🧪 AWDX Test Results Summary")
        table.add_column("Test Suite", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Exit Code", justify="right")
        
        for test_name, result in self.results.items():
            status = "✅ PASSED" if result['success'] else "❌ FAILED"
            table.add_row(
                test_name.title(),
                status,
                str(result['exit_code'])
            )
        
        console.print(table)
        
        # Overall status
        passed_count = sum(1 for result in self.results.values() if result['success'])
        total_count = len(self.results)
        
        if passed_count == total_count:
            console.print(f"\n🎉 [bold green]All {total_count} test suites passed![/bold green]")
            console.print("✅ [green]Codebase is ready for production[/green]")
        else:
            failed_count = total_count - passed_count
            console.print(f"\n⚠️ [yellow]{failed_count} out of {total_count} test suites failed[/yellow]")
            console.print("❌ [red]Review failed tests before production deployment[/red]")


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="AWDX Comprehensive Test Runner")
    parser.add_argument("--security", action="store_true", help="Run security tests only")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    parser.add_argument("--quick", action="store_true", help="Quick mode for security tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--report", type=str, help="Generate detailed report to file")
    parser.add_argument("--install-deps", action="store_true", help="Install test dependencies first")
    
    args = parser.parse_args()
    
    # Default to all tests if no specific test type is selected
    if not any([args.security, args.unit, args.integration]):
        args.all = True
    
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
    
    # Initialize test runner
    runner = TestRunner(project_root)
    
    # Import version dynamically
    try:
        from awdx import __version__
        version_str = __version__
    except ImportError:
        version_str = "0.1.0-dev"
    
    console.print(f"🧪 [bold blue]AWDX Test Runner v{version_str}[/bold blue]")
    console.print(f"📁 Project root: {project_root}")
    console.print()
    
    try:
        # Install dependencies if requested
        if args.install_deps:
            if not runner.install_dependencies():
                console.print("❌ [red]Failed to install dependencies[/red]")
                sys.exit(1)
        
        all_passed = True
        
        # Run security tests
        if args.security or args.all:
            passed = runner.run_security_tests(quick_mode=args.quick, generate_report=bool(args.report))
            all_passed = all_passed and passed
        
        # Run unit tests
        if args.unit or args.all:
            passed = runner.run_unit_tests(coverage=args.coverage)
            all_passed = all_passed and passed
        
        # Run integration tests
        if args.integration or args.all:
            passed = runner.run_integration_tests()
            all_passed = all_passed and passed
        
        # Run code quality checks (always run with --all)
        if args.all:
            passed = runner.run_code_quality_checks()
            all_passed = all_passed and passed
        
        # Display summary
        console.print()
        runner.display_summary()
        
        # Generate report if requested
        if args.report:
            report_file = Path(args.report)
            runner.generate_summary_report(report_file)
        
        # Exit with appropriate code
        sys.exit(0 if all_passed else 1)
        
    except KeyboardInterrupt:
        console.print("\n🛑 [yellow]Tests interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n❌ [red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main() 