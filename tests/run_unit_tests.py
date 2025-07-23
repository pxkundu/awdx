#!/usr/bin/env python3
"""
🧪 AWDX Unit Test Runner
========================

Fast unit test runner for AWDX modules.

Usage:
    python tests/run_unit_tests.py [--coverage] [--verbose]

Options:
    --coverage      Generate coverage report
    --verbose       Verbose output
    --help          Show this help message

Examples:
    python tests/run_unit_tests.py
    python tests/run_unit_tests.py --coverage --verbose
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


def run_unit_tests(coverage: bool = False, verbose: bool = False) -> bool:
    """Run unit tests with pytest."""
    console.print("🧪 [bold blue]Running Unit Tests[/bold blue]")
    
    start_time = time.time()
    
    cmd = [sys.executable, "-m", "pytest"]
    
    # Test configuration - focus on unit tests only
    cmd.extend([
        "tests/",
        "-m", "unit",
        "--strict-markers",
        "--tb=short",
        "-x",  # Stop on first failure
        "--maxfail=5",  # Stop after 5 failures
    ])
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")  # Quiet mode for faster output
    
    if coverage:
        cmd.extend([
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html:coverage_html",
            "--cov-report=xml:coverage.xml",
        ])
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running unit tests...", total=None)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout for unit tests
            )
            
            progress.update(task, completed=True)
        
        elapsed_time = time.time() - start_time
        
        # Display results
        if result.returncode == 0:
            console.print(f"✅ [green]Unit tests passed in {elapsed_time:.2f}s[/green]")
            if result.stdout:
                console.print(result.stdout)
        else:
            console.print(f"❌ [red]Unit tests failed in {elapsed_time:.2f}s[/red]")
            console.print(result.stdout)
            if result.stderr:
                console.print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        console.print("❌ [red]Unit tests timed out[/red]")
        return False
    except Exception as e:
        console.print(f"❌ [red]Error running unit tests: {e}[/red]")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AWDX Unit Test Runner")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
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
    
    console.print(f"🧪 [bold blue]AWDX Unit Test Runner[/bold blue]")
    console.print(f"📁 Project root: {project_root}")
    console.print()
    
    try:
        success = run_unit_tests(coverage=args.coverage, verbose=args.verbose)
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        console.print("\n🛑 [yellow]Tests interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n❌ [red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main() 