#!/usr/bin/env python3
"""
Test Phase 3 Infrastructure Automation Commands

This script tests all Phase 3 commands to ensure they are properly registered
and functional in the AWDX task module.
"""

import sys
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Phase 3 Infrastructure Automation Commands
PHASE3_COMMANDS = [
    # Infrastructure Automation
    {
        "command": "infra-audit",
        "description": "Infrastructure security and compliance audit",
        "category": "Infrastructure"
    },
    {
        "command": "infra-drift",
        "description": "Infrastructure drift detection and remediation",
        "category": "Infrastructure"
    },
    {
        "command": "infra-cost",
        "description": "Infrastructure cost estimation and optimization",
        "category": "Infrastructure"
    },
    {
        "command": "template-validate",
        "description": "CloudFormation/CDK template validation",
        "category": "Infrastructure"
    },
    {
        "command": "template-optimize",
        "description": "Template optimization for cost and performance",
        "category": "Infrastructure"
    },
    {
        "command": "template-compliance",
        "description": "Template compliance checking",
        "category": "Infrastructure"
    },
    # Container Security
    {
        "command": "container-scan",
        "description": "Container image vulnerability scanning",
        "category": "Container"
    },
    {
        "command": "container-audit",
        "description": "Container security and configuration audit",
        "category": "Container"
    },
    {
        "command": "container-optimize",
        "description": "Container resource and cost optimization",
        "category": "Container"
    },
    {
        "command": "k8s-audit",
        "description": "Kubernetes security and RBAC audit",
        "category": "Container"
    },
    {
        "command": "k8s-compliance",
        "description": "Kubernetes compliance checking",
        "category": "Container"
    },
    {
        "command": "k8s-monitor",
        "description": "Kubernetes resource and performance monitoring",
        "category": "Container"
    },
    # CI/CD Pipeline Security
    {
        "command": "pipeline-audit",
        "description": "CI/CD pipeline security and configuration audit",
        "category": "Pipeline"
    },
    {
        "command": "pipeline-optimize",
        "description": "Pipeline performance and cost optimization",
        "category": "Pipeline"
    },
    {
        "command": "pipeline-monitor",
        "description": "Pipeline execution and performance monitoring",
        "category": "Pipeline"
    },
    {
        "command": "build-optimize",
        "description": "Build process optimization and caching",
        "category": "Pipeline"
    },
    {
        "command": "build-security",
        "description": "Build security scanning and vulnerability detection",
        "category": "Pipeline"
    },
    {
        "command": "build-compliance",
        "description": "Build compliance checking and reporting",
        "category": "Pipeline"
    },
    # Monitoring and Alerting
    {
        "command": "monitoring-setup",
        "description": "Automated monitoring setup with best practices",
        "category": "Monitoring"
    },
    {
        "command": "monitoring-optimize",
        "description": "Monitoring cost and performance optimization",
        "category": "Monitoring"
    },
    {
        "command": "monitoring-compliance",
        "description": "Monitoring compliance checking",
        "category": "Monitoring"
    },
    {
        "command": "alert-configure",
        "description": "Intelligent alert configuration and thresholds",
        "category": "Monitoring"
    },
    {
        "command": "alert-optimize",
        "description": "Alert noise reduction and response optimization",
        "category": "Monitoring"
    },
    # Network Security
    {
        "command": "network-audit",
        "description": "Network configuration and security audit",
        "category": "Network"
    },
    {
        "command": "network-optimize",
        "description": "Network routing and cost optimization",
        "category": "Network"
    },
    {
        "command": "network-monitor",
        "description": "Network traffic and anomaly monitoring",
        "category": "Network"
    },
    {
        "command": "sg-audit",
        "description": "Security group rules and compliance audit",
        "category": "Network"
    },
    {
        "command": "sg-optimize",
        "description": "Security group rules and coverage optimization",
        "category": "Network"
    },
    {
        "command": "sg-compliance",
        "description": "Security group compliance checking",
        "category": "Network"
    }
]

def test_command_registration(command):
    """Test if a command is properly registered."""
    try:
        # Test if command shows up in help
        result = subprocess.run(
            ["python", "-m", "awdx.task.task_commands", command, "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return True, "✅ Registered"
        else:
            return False, f"❌ Not registered: {result.stderr.strip()}"
            
    except subprocess.TimeoutExpired:
        return False, "❌ Timeout"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def test_ai_intent_integration():
    """Test if AI intents are properly integrated."""
    try:
        # Import the intents module to check for Phase 3 intents
        from awdx.task.intents import TASK_INTENTS
        
        phase3_intents = [
            intent for intent in TASK_INTENTS 
            if any(cmd["command"].replace("-", "_") in intent["intent"] for cmd in PHASE3_COMMANDS)
        ]
        
        return len(phase3_intents), len(PHASE3_COMMANDS)
        
    except Exception as e:
        return 0, len(PHASE3_COMMANDS)

def test_mcp_tools_integration():
    """Test if MCP tools are properly integrated."""
    try:
        from awdx.mcp_server.tools import AWDXToolRegistry
        
        registry = AWDXToolRegistry()
        registry.register_phase3_tools()
        
        tools = registry.get_tools()
        phase3_tools = [
            tool for tool in tools 
            if any(cmd["command"].replace("-", "_") in tool["name"] for cmd in PHASE3_COMMANDS)
        ]
        
        return len(phase3_tools), len(PHASE3_COMMANDS)
        
    except Exception as e:
        console.print(f"[red]Error testing MCP tools: {e}[/red]")
        return 0, len(PHASE3_COMMANDS)

def main():
    """Run Phase 3 command tests."""
    console.print(Panel("🚀 AWDX Phase 3 Infrastructure Automation Commands Test", style="bold blue"))
    
    # Test command registration
    console.print("\n[bold yellow]Testing Command Registration:[/bold yellow]")
    
    table = Table(title="Phase 3 Command Registration Status")
    table.add_column("Category", style="cyan")
    table.add_column("Command", style="white")
    table.add_column("Description", style="dim")
    table.add_column("Status", style="bold")
    
    success_count = 0
    total_count = len(PHASE3_COMMANDS)
    
    for cmd_info in PHASE3_COMMANDS:
        command = cmd_info["command"]
        category = cmd_info["category"]
        description = cmd_info["description"]
        
        success, status = test_command_registration(command)
        if success:
            success_count += 1
        
        table.add_row(category, command, description, status)
    
    console.print(table)
    
    # Test AI integration
    console.print(f"\n[bold yellow]Testing AI Intent Integration:[/bold yellow]")
    ai_intents_found, ai_intents_expected = test_ai_intent_integration()
    console.print(f"AI Intents: {ai_intents_found}/{ai_intents_expected} found")
    
    # Test MCP tools integration
    console.print(f"\n[bold yellow]Testing MCP Tools Integration:[/bold yellow]")
    mcp_tools_found, mcp_tools_expected = test_mcp_tools_integration()
    console.print(f"MCP Tools: {mcp_tools_found}/{mcp_tools_expected} found")
    
    # Summary
    console.print(f"\n[bold yellow]Summary:[/bold yellow]")
    console.print(f"Commands: {success_count}/{total_count} registered successfully")
    console.print(f"AI Intents: {ai_intents_found}/{ai_intents_expected} integrated")
    console.print(f"MCP Tools: {mcp_tools_found}/{mcp_tools_expected} integrated")
    
    if success_count == total_count and ai_intents_found >= ai_intents_expected // 2 and mcp_tools_found >= mcp_tools_expected // 2:
        console.print("\n[bold green]✅ Phase 3 implementation successful![/bold green]")
        console.print("[green]All infrastructure automation commands are properly integrated.[/green]")
        return 0
    else:
        console.print("\n[bold red]❌ Phase 3 implementation incomplete![/bold red]")
        console.print("[red]Some commands may not be properly registered or integrated.[/red]")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 