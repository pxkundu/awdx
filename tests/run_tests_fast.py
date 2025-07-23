#!/usr/bin/env python3
"""
🚀 AWDX Fast Test Runner
========================

Quick test runner with multiple options for different testing needs.

Usage:
    python tests/run_tests_fast.py [option]

Options:
    unit          Run only unit tests (fastest)
    integration   Run only integration tests
    security      Run only security tests
    quick         Run all tests in parallel (recommended)
    all           Run all tests sequentially (comprehensive)
    help          Show this help message

Examples:
    python tests/run_tests_fast.py unit
    python tests/run_tests_fast.py quick
    python tests/run_tests_fast.py all
"""

import subprocess
import sys
from pathlib import Path

def show_help():
    """Show help message."""
    print(__doc__)

def run_command(script_name: str) -> bool:
    """Run a test script."""
    script_path = Path("tests") / script_name
    
    if not script_path.exists():
        print(f"❌ Test script not found: {script_path}")
        return False
    
    try:
        result = subprocess.run([sys.executable, str(script_path)], check=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def main():
    """Main entry point."""
    if len(sys.argv) != 2 or sys.argv[1] in ['help', '--help', '-h']:
        show_help()
        sys.exit(0)
    
    option = sys.argv[1].lower()
    
    # Map options to scripts
    script_map = {
        'unit': 'run_unit_tests.py',
        'integration': 'run_integration_tests.py', 
        'security': 'run_security_tests.py',
        'quick': 'run_quick_tests.py',
        'all': 'run_tests.py'
    }
    
    if option not in script_map:
        print(f"❌ Unknown option: {option}")
        print("Use 'python tests/run_tests_fast.py help' for available options")
        sys.exit(1)
    
    script_name = script_map[option]
    print(f"🚀 Running {option} tests...")
    
    success = run_command(script_name)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 