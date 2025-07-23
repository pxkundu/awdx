#!/usr/bin/env python3
"""
⚡ AWDX Quick Test Runner
=========================

Fast parallel test runner for AWDX modules.

Usage:
    python tests/run_quick_tests.py [--parallel] [--verbose]

Options:
    --parallel      Run tests in parallel (default)
    --sequential    Run tests sequentially
    --verbose       Verbose output
    --help          Show this help message

Examples:
    python tests/run_quick_tests.py
    python tests/run_quick_tests.py --sequential --verbose
"""

import argparse
import concurrent.futures
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.table import Table
except ImportError:
    print("❌ Missing dependencies. Install with: pip install -e '.[test]'")
    sys.exit(1)

console = Console()


def run_test_command(cmd: List[str], test_name: str, timeout: int = 300) -> Tuple[str, bool, str, float]:
    """Run a test command and return results."""
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        
        elapsed_time = time.time() - start_time
        success = result.returncode == 0
        output = result.stdout + result.stderr
        
        return test_name, success, output, elapsed_time
        
    except subprocess.TimeoutExpired:
        elapsed_time = time.time() - start_time
        return test_name, False, f"Test timed out after {timeout}s", elapsed_time
    except Exception as e:
        elapsed_time = time.time() - start_time
        return test_name, False, f"Error: {e}", elapsed_time


def run_tests_parallel() -> Dict[str, Tuple[bool, str, float]]:
    """Run all tests in parallel."""
    console.print("⚡ [bold blue]Running Tests in Parallel[/bold blue]")
    
    # Define test commands
    test_commands = [
        {
            "name": "Unit Tests",
            "cmd": [sys.executable, "-m", "pytest", "tests/", "-m", "unit", "--strict-markers", "--tb=short", "-q"],
            "timeout": 120
        },
        {
            "name": "Integration Tests", 
            "cmd": [sys.executable, "-m", "pytest", "tests/", "-m", "integration", "--strict-markers", "--tb=short", "-q"],
            "timeout": 180
        },
        {
            "name": "Security Tests",
            "cmd": [sys.executable, "-m", "pytest", "tests/", "-m", "security", "--strict-markers", "--tb=short", "-q"],
            "timeout": 120
        },
        {
            "name": "Security Scanner",
            "cmd": [sys.executable, "tests/security_scanner.py", "--quick"],
            "timeout": 180
        }
    ]
    
    results = {}
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        
        # Create tasks for each test
        tasks = {}
        for test in test_commands:
            task = progress.add_task(f"Running {test['name']}...", total=None)
            tasks[test['name']] = task
        
        # Run tests in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_test = {
                executor.submit(run_test_command, test["cmd"], test["name"], test["timeout"]): test["name"]
                for test in test_commands
            }
            
            for future in concurrent.futures.as_completed(future_to_test):
                test_name, success, output, elapsed_time = future.result()
                progress.update(tasks[test_name], completed=True)
                results[test_name] = (success, output, elapsed_time)
    
    return results


def run_tests_sequential() -> Dict[str, Tuple[bool, str, float]]:
    """Run all tests sequentially."""
    console.print("⚡ [bold blue]Running Tests Sequentially[/bold blue]")
    
    # Define test commands
    test_commands = [
        {
            "name": "Unit Tests",
            "cmd": [sys.executable, "-m", "pytest", "tests/", "-m", "unit", "--strict-markers", "--tb=short", "-q"],
            "timeout": 120
        },
        {
            "name": "Integration Tests", 
            "cmd": [sys.executable, "-m", "pytest", "tests/", "-m", "integration", "--strict-markers", "--tb=short", "-q"],
            "timeout": 180
        },
        {
            "name": "Security Tests",
            "cmd": [sys.executable, "-m", "pytest", "tests/", "-m", "security", "--strict-markers", "--tb=short", "-q"],
            "timeout": 120
        },
        {
            "name": "Security Scanner",
            "cmd": [sys.executable, "tests/security_scanner.py", "--quick"],
            "timeout": 180
        }
    ]
    
    results = {}
    
    for test in test_commands:
        console.print(f"🧪 Running {test['name']}...")
        test_name, success, output, elapsed_time = run_test_command(
            test["cmd"], test["name"], test["timeout"]
        )
        results[test_name] = (success, output, elapsed_time)
        
        if success:
            console.print(f"✅ {test_name} passed in {elapsed_time:.2f}s")
        else:
            console.print(f"❌ {test_name} failed in {elapsed_time:.2f}s")
    
    return results


def display_results(results: Dict[str, Tuple[bool, str, float]], verbose: bool = False):
    """Display test results in a table."""
    table = Table(title="🧪 AWDX Quick Test Results")
    table.add_column("Test", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Time", justify="right")
    table.add_column("Details")
    
    total_time = 0
    passed_count = 0
    
    for test_name, (success, output, elapsed_time) in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        time_str = f"{elapsed_time:.2f}s"
        
        # Truncate output for table
        details = output[:100] + "..." if len(output) > 100 else output
        if not verbose:
            details = "See output above" if output else ""
        
        table.add_row(test_name, status, time_str, details)
        
        total_time += elapsed_time
        if success:
            passed_count += 1
    
    console.print(table)
    
    # Summary
    total_count = len(results)
    console.print(f"\n📊 Summary: {passed_count}/{total_count} tests passed in {total_time:.2f}s")
    
    if passed_count == total_count:
        console.print("🎉 [bold green]All tests passed![/bold green]")
    else:
        failed_count = total_count - passed_count
        console.print(f"❌ [bold red]{failed_count} test(s) failed[/bold red]")
    
    # Show detailed output if verbose
    if verbose:
        console.print("\n📋 Detailed Output:")
        for test_name, (success, output, elapsed_time) in results.items():
            if output:
                console.print(f"\n### {test_name}")
                console.print(f"Time: {elapsed_time:.2f}s")
                console.print(f"Status: {'✅ PASSED' if success else '❌ FAILED'}")
                console.print("Output:")
                console.print(Panel(output, title=f"{test_name} Output"))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AWDX Quick Test Runner")
    parser.add_argument("--parallel", action="store_true", default=True, help="Run tests in parallel (default)")
    parser.add_argument("--sequential", action="store_true", help="Run tests sequentially")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Handle parallel vs sequential
    if args.sequential:
        args.parallel = False
    
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
    
    console.print(f"⚡ [bold blue]AWDX Quick Test Runner[/bold blue]")
    console.print(f"📁 Project root: {project_root}")
    console.print(f"🔧 Mode: {'Parallel' if args.parallel else 'Sequential'}")
    console.print()
    
    try:
        start_time = time.time()
        
        if args.parallel:
            results = run_tests_parallel()
        else:
            results = run_tests_sequential()
        
        total_time = time.time() - start_time
        
        console.print()
        display_results(results, verbose=args.verbose)
        
        # Exit with appropriate code
        passed_count = sum(1 for success, _, _ in results.values())
        total_count = len(results)
        
        sys.exit(0 if passed_count == total_count else 1)
        
    except KeyboardInterrupt:
        console.print("\n🛑 [yellow]Tests interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n❌ [red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main() 