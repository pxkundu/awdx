#!/usr/bin/env python3
"""
Test script for Phase 2 commands in AWDX task module.

This script tests the new service-specific commands:
- lambda-audit, lambda-optimize, lambda-monitor
- iam-audit, iam-optimize  
- s3-audit, s3-optimize
"""

import json
import subprocess
import sys
import time
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Add the src directory to the path
sys.path.insert(0, 'src')

def run_command(cmd: str) -> Dict[str, Any]:
    """Run an AWDX command and return the result."""
    try:
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command timed out",
            "returncode": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }

def test_help_command():
    """Test that the help command shows Phase 2 commands."""
    print("🔍 Testing help command...")
    
    result = run_command("awdx task help")
    
    if result["success"]:
        help_text = result["stdout"]
        
        # Check for Phase 2 commands in help
        phase2_commands = [
            "lambda-audit",
            "lambda-optimize", 
            "lambda-monitor",
            "iam-audit",
            "iam-optimize",
            "s3-audit",
            "s3-optimize"
        ]
        
        missing_commands = []
        for cmd in phase2_commands:
            if cmd not in help_text:
                missing_commands.append(cmd)
        
        if missing_commands:
            print(f"❌ Missing Phase 2 commands in help: {missing_commands}")
            return False
        else:
            print("✅ All Phase 2 commands found in help")
            return True
    else:
        print(f"❌ Help command failed: {result['stderr']}")
        return False

def test_lambda_commands():
    """Test Lambda-related commands."""
    print("\n🔍 Testing Lambda commands...")
    
    # Test lambda-audit
    print("  Testing lambda-audit...")
    result = run_command("awdx task lambda-audit --help")
    if result["success"]:
        print("  ✅ lambda-audit command works")
    else:
        print(f"  ❌ lambda-audit failed: {result['stderr']}")
    
    # Test lambda-optimize
    print("  Testing lambda-optimize...")
    result = run_command("awdx task lambda-optimize --help")
    if result["success"]:
        print("  ✅ lambda-optimize command works")
    else:
        print(f"  ❌ lambda-optimize failed: {result['stderr']}")
    
    # Test lambda-monitor
    print("  Testing lambda-monitor...")
    result = run_command("awdx task lambda-monitor")
    if result["success"]:
        print("  ✅ lambda-monitor command works")
    else:
        print(f"  ❌ lambda-monitor failed: {result['stderr']}")

def test_iam_commands():
    """Test IAM-related commands."""
    print("\n🔍 Testing IAM commands...")
    
    # Test iam-audit
    print("  Testing iam-audit...")
    result = run_command("awdx task iam-audit --help")
    if result["success"]:
        print("  ✅ iam-audit command works")
    else:
        print(f"  ❌ iam-audit failed: {result['stderr']}")
    
    # Test iam-optimize
    print("  Testing iam-optimize...")
    result = run_command("awdx task iam-optimize --help")
    if result["success"]:
        print("  ✅ iam-optimize command works")
    else:
        print(f"  ❌ iam-optimize failed: {result['stderr']}")

def test_s3_commands():
    """Test S3-related commands."""
    print("\n🔍 Testing S3 commands...")
    
    # Test s3-audit
    print("  Testing s3-audit...")
    result = run_command("awdx task s3-audit --help")
    if result["success"]:
        print("  ✅ s3-audit command works")
    else:
        print(f"  ❌ s3-audit failed: {result['stderr']}")
    
    # Test s3-optimize
    print("  Testing s3-optimize...")
    result = run_command("awdx task s3-optimize --help")
    if result["success"]:
        print("  ✅ s3-optimize command works")
    else:
        print(f"  ❌ s3-optimize failed: {result['stderr']}")

def test_ai_intents():
    """Test that AI intents include Phase 2 commands."""
    print("\n🔍 Testing AI intents...")
    
    try:
        from awdx.task.intents import TASK_INTENTS
        
        # Check for Phase 2 intents
        phase2_intents = [
            "lambda_audit",
            "lambda_optimize",
            "lambda_monitor",
            "iam_audit",
            "iam_optimize",
            "s3_audit",
            "s3_optimize"
        ]
        
        found_intents = []
        for intent in TASK_INTENTS:
            if intent["intent"] in phase2_intents:
                found_intents.append(intent["intent"])
        
        missing_intents = [intent for intent in phase2_intents if intent not in found_intents]
        
        if missing_intents:
            print(f"❌ Missing AI intents: {missing_intents}")
            return False
        else:
            print("✅ All Phase 2 AI intents found")
            return True
            
    except ImportError as e:
        print(f"❌ Could not import AI intents: {e}")
        return False

def test_mcp_tools():
    """Test that MCP tools include Phase 2 commands."""
    print("\n🔍 Testing MCP tools...")
    
    try:
        from awdx.mcp_server.tools import AWDXToolRegistry
        
        # Create tool registry
        registry = AWDXToolRegistry()
        registry.register_phase2_tools()
        
        # Get all tools
        tools = registry.get_tools()
        tool_names = [tool["name"] for tool in tools]
        
        # Check for Phase 2 tools
        phase2_tools = [
            "awdx_lambda_audit",
            "awdx_lambda_optimize",
            "awdx_lambda_monitor",
            "awdx_iam_audit_comprehensive",
            "awdx_iam_optimize",
            "awdx_s3_audit_comprehensive",
            "awdx_s3_optimize"
        ]
        
        missing_tools = [tool for tool in phase2_tools if tool not in tool_names]
        
        if missing_tools:
            print(f"❌ Missing MCP tools: {missing_tools}")
            return False
        else:
            print("✅ All Phase 2 MCP tools found")
            return True
            
    except ImportError as e:
        print(f"❌ Could not import MCP tools: {e}")
        return False

def main():
    """Run all Phase 2 command tests."""
    print("🚀 AWDX Phase 2 Commands Test Suite")
    print("=" * 50)
    
    start_time = time.time()
    
    # Test help command
    help_success = test_help_command()
    
    # Test Lambda commands
    test_lambda_commands()
    
    # Test IAM commands
    test_iam_commands()
    
    # Test S3 commands
    test_s3_commands()
    
    # Test AI intents
    ai_success = test_ai_intents()
    
    # Test MCP tools
    mcp_success = test_mcp_tools()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print(f"✅ Help command: {'PASS' if help_success else 'FAIL'}")
    print(f"✅ AI intents: {'PASS' if ai_success else 'FAIL'}")
    print(f"✅ MCP tools: {'PASS' if mcp_success else 'FAIL'}")
    
    if help_success and ai_success and mcp_success:
        print("\n🎉 All Phase 2 command tests passed!")
        return 0
    else:
        print("\n❌ Some Phase 2 command tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 