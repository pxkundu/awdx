#!/usr/bin/env python3
"""
🔒 AWDX Security Test Runner
============================

Security test runner for AWDX modules.

Usage:
    python tests/run_security_tests.py [--quick] [--verbose] [--report]

Options:
    --quick         Quick security scan mode
    --verbose       Verbose output
    --report        Generate detailed report
    --help          Show this help message

Examples:
    python tests/run_security_tests.py
    python tests/run_security_tests.py --quick --verbose
    python tests/run_security_tests.py --report security_report.md
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
except ImportError:
    print("❌ Missing dependencies. Install with: pip install -e '.[test]'")
    sys.exit(1)

console = Console()


def run_security_tests(quick_mode: bool = False, verbose: bool = False, generate_report: bool = False) -> bool:
    """Run security scanning tests."""
    console.print("🔒 [bold blue]Running Security Tests[/bold blue]")
    
    start_time = time.time()
    
    # Run security scanner
    security_script = Path("tests") / "security_scanner.py"
    if not security_script.exists():
        console.print("❌ Security scanner not found!")
        return False
    
    cmd = [sys.executable, str(security_script)]
    if quick_mode:
        cmd.append("--quick")
    if generate_report:
        cmd.extend(["--report", "security_report.md"])
    if verbose:
        cmd.append("--verbose")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running security tests...", total=None)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180,  # 3 minute timeout for security tests
            )
            
            progress.update(task, completed=True)
        
        elapsed_time = time.time() - start_time
        
        # Display results
        if result.returncode == 0:
            console.print(f"✅ [green]Security tests passed in {elapsed_time:.2f}s[/green]")
            if result.stdout:
                console.print(result.stdout)
        else:
            console.print(f"❌ [red]Security tests failed in {elapsed_time:.2f}s[/red]")
            console.print(result.stdout)
            if result.stderr:
                console.print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        console.print("❌ [red]Security tests timed out[/red]")
        return False
    except Exception as e:
        console.print(f"❌ [red]Error running security tests: {e}[/red]")
        return False


def run_security_unit_tests(verbose: bool = False) -> bool:
    """Run security unit tests with pytest."""
    console.print("🔒 [bold blue]Running Security Unit Tests[/bold blue]")
    
    start_time = time.time()
    
    cmd = [sys.executable, "-m", "pytest"]
    
    # Test configuration - focus on fast security tests only
    cmd.extend([
        "tests/test_security_scanner_fast.py",
        "-m", "security",
        "--strict-markers",
        "--tb=short",
        "-x",  # Stop on first failure
        "--maxfail=3",  # Stop after 3 failures
    ])
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")  # Quiet mode for faster output
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running security unit tests...", total=None)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout for security unit tests
            )
            
            progress.update(task, completed=True)
        
        elapsed_time = time.time() - start_time
        
        # Display results
        if result.returncode == 0:
            console.print(f"✅ [green]Security unit tests passed in {elapsed_time:.2f}s[/green]")
            if result.stdout:
                console.print(result.stdout)
        else:
            console.print(f"❌ [red]Security unit tests failed in {elapsed_time:.2f}s[/red]")
            console.print(result.stdout)
            if result.stderr:
                console.print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        console.print("❌ [red]Security unit tests timed out[/red]")
        return False
    except Exception as e:
        console.print(f"❌ [red]Error running security unit tests: {e}[/red]")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AWDX Security Test Runner")
    parser.add_argument("--quick", action="store_true", help="Quick security scan mode")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    parser.add_argument("--unit-only", action="store_true", help="Run only security unit tests")
    parser.add_argument("--scanner-only", action="store_true", help="Run only security scanner")
    
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
    
    # Change to project root
    import os
    os.chdir(project_root)
    
    console.print(f"🔒 [bold blue]AWDX Security Test Runner[/bold blue]")
    console.print(f"📁 Project root: {project_root}")
    console.print()
    
    try:
        all_passed = True
        
        # Run security scanner tests
        if not args.unit_only:
            passed = run_security_tests(
                quick_mode=args.quick,
                verbose=args.verbose,
                generate_report=args.report
            )
            all_passed = all_passed and passed
        
        # Run security unit tests
        if not args.scanner_only:
            passed = run_security_unit_tests(verbose=args.verbose)
            all_passed = all_passed and passed
        
        # Display summary
        if all_passed:
            console.print("\n🎉 [bold green]All security tests passed![/bold green]")
        else:
            console.print("\n❌ [bold red]Some security tests failed![/bold red]")
        
        sys.exit(0 if all_passed else 1)
        
    except KeyboardInterrupt:
        console.print("\n🛑 [yellow]Tests interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n❌ [red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main() 