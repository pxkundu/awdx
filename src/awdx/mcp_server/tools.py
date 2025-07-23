"""
AWDX MCP Tools Implementation

This module implements MCP tools that expose AWDX capabilities to AI assistants
through the Model Context Protocol.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

from ..ai_engine.nlp_processor import NLPProcessor
# Import command modules (these are Typer apps, not classes)
from ..profilyze import profile_commands
from ..costlyzer import cost_commands
from ..iamply import iam_commands
from ..s3ntry import s3_commands
from ..secrex import secret_commands
from ..secutide import security_commands

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Represents an MCP tool definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: callable


class AWDXToolRegistry:
    """
    Registry for AWDX MCP tools.
    
    This class manages the registration and execution of AWDX tools
    that can be called by AI assistants through the MCP protocol.
    """

    def __init__(self):
        """Initialize the tool registry."""
        self.tools: Dict[str, MCPTool] = {}
        # Command handlers will be implemented as direct function calls
        # since the modules use Typer apps rather than classes
        self.command_handlers = {}

    def register_tool(self, tool: MCPTool) -> None:
        """Register an MCP tool."""
        self.tools[tool.name] = tool
        logger.debug(f"Registered MCP tool: {tool.name}")

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get all registered tools in MCP format."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            }
            for tool in self.tools.values()
        ]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a registered tool with arguments."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")
        
        tool = self.tools[tool_name]
        try:
            result = await tool.handler(arguments)
            return result
        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {e}")
            raise

    def register_profile_tools(self) -> None:
        """Register profile management tools."""
        tools = [
            MCPTool(
                name="awdx_profile_list",
                description="List all AWS profiles configured in AWDX",
                input_schema={
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "enum": ["table", "json", "csv"],
                            "description": "Output format"
                        }
                    }
                },
                handler=self._handle_profile_list
            ),
            MCPTool(
                name="awdx_profile_switch",
                description="Switch to a different AWS profile",
                input_schema={
                    "type": "object",
                    "properties": {
                        "profile_name": {
                            "type": "string",
                            "description": "Name of the profile to switch to"
                        }
                    },
                    "required": ["profile_name"]
                },
                handler=self._handle_profile_switch
            ),
            MCPTool(
                name="awdx_profile_add",
                description="Add a new AWS profile",
                input_schema={
                    "type": "object",
                    "properties": {
                        "profile_name": {
                            "type": "string",
                            "description": "Name for the new profile"
                        },
                        "access_key": {
                            "type": "string",
                            "description": "AWS access key ID"
                        },
                        "secret_key": {
                            "type": "string",
                            "description": "AWS secret access key"
                        },
                        "region": {
                            "type": "string",
                            "description": "AWS region"
                        }
                    },
                    "required": ["profile_name"]
                },
                handler=self._handle_profile_add
            )
        ]
        
        for tool in tools:
            self.register_tool(tool)

    def register_cost_tools(self) -> None:
        """Register cost analysis tools."""
        tools = [
            MCPTool(
                name="awdx_cost_summary",
                description="Get AWS cost summary and analysis",
                input_schema={
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Number of days to analyze",
                            "default": 30
                        },
                        "service": {
                            "type": "string",
                            "description": "Specific AWS service to analyze"
                        },
                        "profile": {
                            "type": "string",
                            "description": "AWS profile to use"
                        }
                    }
                },
                handler=self._handle_cost_summary
            ),
            MCPTool(
                name="awdx_cost_trends",
                description="Analyze cost trends over time",
                input_schema={
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Number of days to analyze",
                            "default": 90
                        },
                        "granularity": {
                            "type": "string",
                            "enum": ["daily", "weekly", "monthly"],
                            "description": "Time granularity for analysis"
                        }
                    }
                },
                handler=self._handle_cost_trends
            ),
            MCPTool(
                name="awdx_cost_optimize",
                description="Get cost optimization recommendations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "threshold": {
                            "type": "number",
                            "description": "Minimum cost threshold for recommendations"
                        },
                        "include_risks": {
                            "type": "boolean",
                            "description": "Include potential risks in recommendations"
                        }
                    }
                },
                handler=self._handle_cost_optimize
            )
        ]
        
        for tool in tools:
            self.register_tool(tool)

    def register_iam_tools(self) -> None:
        """Register IAM security tools."""
        tools = [
            MCPTool(
                name="awdx_iam_audit",
                description="Perform comprehensive IAM security audit",
                input_schema={
                    "type": "object",
                    "properties": {
                        "checks": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific checks to perform"
                        },
                        "output_format": {
                            "type": "string",
                            "enum": ["json", "csv", "report"],
                            "description": "Output format"
                        }
                    }
                },
                handler=self._handle_iam_audit
            ),
            MCPTool(
                name="awdx_iam_users",
                description="List and analyze IAM users",
                input_schema={
                    "type": "object",
                    "properties": {
                        "filters": {
                            "type": "object",
                            "description": "Filters to apply to user list"
                        },
                        "include_details": {
                            "type": "boolean",
                            "description": "Include detailed user information"
                        }
                    }
                },
                handler=self._handle_iam_users
            ),
            MCPTool(
                name="awdx_iam_roles",
                description="List and analyze IAM roles",
                input_schema={
                    "type": "object",
                    "properties": {
                        "role_type": {
                            "type": "string",
                            "enum": ["all", "service", "user"],
                            "description": "Type of roles to list"
                        }
                    }
                },
                handler=self._handle_iam_roles
            )
        ]
        
        for tool in tools:
            self.register_tool(tool)

    def register_s3_tools(self) -> None:
        """Register S3 security tools."""
        tools = [
            MCPTool(
                name="awdx_s3_audit",
                description="Perform S3 bucket security audit",
                input_schema={
                    "type": "object",
                    "properties": {
                        "bucket_name": {
                            "type": "string",
                            "description": "Specific bucket to audit"
                        },
                        "checks": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Security checks to perform"
                        }
                    }
                },
                handler=self._handle_s3_audit
            ),
            MCPTool(
                name="awdx_s3_scan",
                description="Scan S3 buckets for security issues",
                input_schema={
                    "type": "object",
                    "properties": {
                        "scan_type": {
                            "type": "string",
                            "enum": ["public", "encryption", "logging", "all"],
                            "description": "Type of security scan"
                        }
                    }
                },
                handler=self._handle_s3_scan
            )
        ]
        
        for tool in tools:
            self.register_tool(tool)

    def register_secret_tools(self) -> None:
        """Register secret management tools."""
        tools = [
            MCPTool(
                name="awdx_secret_discover",
                description="Discover secrets in AWS resources",
                input_schema={
                    "type": "object",
                    "properties": {
                        "resource_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Types of resources to scan"
                        }
                    }
                },
                handler=self._handle_secret_discover
            ),
            MCPTool(
                name="awdx_secret_rotate",
                description="Rotate secrets and credentials",
                input_schema={
                    "type": "object",
                    "properties": {
                        "secret_type": {
                            "type": "string",
                            "enum": ["database", "api", "service", "all"],
                            "description": "Type of secrets to rotate"
                        }
                    }
                },
                handler=self._handle_secret_rotate
            )
        ]
        
        for tool in tools:
            self.register_tool(tool)

    def register_security_tools(self) -> None:
        """Register security assessment tools."""
        tools = [
            MCPTool(
                name="awdx_security_audit",
                description="Perform comprehensive security audit",
                input_schema={
                    "type": "object",
                    "properties": {
                        "scope": {
                            "type": "string",
                            "enum": ["full", "iam", "network", "data"],
                            "description": "Scope of security audit"
                        }
                    }
                },
                handler=self._handle_security_audit
            ),
            MCPTool(
                name="awdx_security_scan",
                description="Scan for security vulnerabilities",
                input_schema={
                    "type": "object",
                    "properties": {
                        "scan_type": {
                            "type": "string",
                            "enum": ["vulnerability", "compliance", "threat"],
                            "description": "Type of security scan"
                        }
                    }
                },
                handler=self._handle_security_scan
            )
        ]
        
        for tool in tools:
            self.register_tool(tool)

    def register_phase2_tools(self) -> None:
        """Register Phase 2 service-specific tools."""
        tools = [
            MCPTool(
                name="awdx_lambda_audit",
                description="Perform comprehensive Lambda function security audit",
                input_schema={
                    "type": "object",
                    "properties": {
                        "security": {
                            "type": "boolean",
                            "description": "Audit Lambda security configurations"
                        },
                        "permissions": {
                            "type": "boolean",
                            "description": "Audit IAM permissions and roles"
                        },
                        "runtime": {
                            "type": "boolean",
                            "description": "Audit runtime configurations and dependencies"
                        }
                    }
                },
                handler=self._handle_lambda_audit
            ),
            MCPTool(
                name="awdx_lambda_optimize",
                description="Optimize Lambda function performance and cost",
                input_schema={
                    "type": "object",
                    "properties": {
                        "memory": {
                            "type": "boolean",
                            "description": "Optimize memory allocation"
                        },
                        "timeout": {
                            "type": "boolean",
                            "description": "Optimize timeout configurations"
                        },
                        "cold_start": {
                            "type": "boolean",
                            "description": "Optimize cold start performance"
                        },
                        "auto_fix": {
                            "type": "boolean",
                            "description": "Automatically apply optimizations"
                        }
                    }
                },
                handler=self._handle_lambda_optimize
            ),
            MCPTool(
                name="awdx_lambda_monitor",
                description="Monitor Lambda function performance, errors, and costs",
                input_schema={
                    "type": "object",
                    "properties": {
                        "performance": {
                            "type": "boolean",
                            "description": "Monitor Lambda performance metrics"
                        },
                        "errors": {
                            "type": "boolean",
                            "description": "Monitor Lambda error rates and logs"
                        },
                        "cost": {
                            "type": "boolean",
                            "description": "Monitor Lambda cost metrics"
                        },
                        "continuous": {
                            "type": "boolean",
                            "description": "Run continuous monitoring"
                        }
                    }
                },
                handler=self._handle_lambda_monitor
            ),
            MCPTool(
                name="awdx_iam_audit_comprehensive",
                description="Perform comprehensive IAM security audit with users, roles, and policies",
                input_schema={
                    "type": "object",
                    "properties": {
                        "users": {
                            "type": "boolean",
                            "description": "Audit IAM users and their permissions"
                        },
                        "roles": {
                            "type": "boolean",
                            "description": "Audit IAM roles and their permissions"
                        },
                        "policies": {
                            "type": "boolean",
                            "description": "Audit IAM policies and their usage"
                        },
                        "compliance": {
                            "type": "boolean",
                            "description": "Check compliance with security standards"
                        }
                    }
                },
                handler=self._handle_iam_audit_comprehensive
            ),
            MCPTool(
                name="awdx_iam_optimize",
                description="Optimize IAM permissions and access management",
                input_schema={
                    "type": "object",
                    "properties": {
                        "permissions": {
                            "type": "boolean",
                            "description": "Optimize IAM permissions"
                        },
                        "least_privilege": {
                            "type": "boolean",
                            "description": "Apply least privilege principle"
                        },
                        "rotation": {
                            "type": "boolean",
                            "description": "Optimize credential rotation"
                        },
                        "auto_fix": {
                            "type": "boolean",
                            "description": "Automatically apply optimizations"
                        }
                    }
                },
                handler=self._handle_iam_optimize
            ),
            MCPTool(
                name="awdx_s3_audit_comprehensive",
                description="Perform comprehensive S3 security audit",
                input_schema={
                    "type": "object",
                    "properties": {
                        "buckets": {
                            "type": "boolean",
                            "description": "Audit S3 bucket configurations"
                        },
                        "policies": {
                            "type": "boolean",
                            "description": "Audit S3 bucket policies"
                        },
                        "encryption": {
                            "type": "boolean",
                            "description": "Audit S3 encryption settings"
                        },
                        "compliance": {
                            "type": "boolean",
                            "description": "Check compliance with data protection standards"
                        }
                    }
                },
                handler=self._handle_s3_audit_comprehensive
            ),
            MCPTool(
                name="awdx_s3_optimize",
                description="Optimize S3 storage, access, and costs",
                input_schema={
                    "type": "object",
                    "properties": {
                        "storage": {
                            "type": "boolean",
                            "description": "Optimize S3 storage classes and lifecycle"
                        },
                        "access": {
                            "type": "boolean",
                            "description": "Optimize S3 access patterns and permissions"
                        },
                        "cost": {
                            "type": "boolean",
                            "description": "Optimize S3 costs and billing"
                        },
                        "auto_fix": {
                            "type": "boolean",
                            "description": "Automatically apply optimizations"
                        }
                    }
                },
                handler=self._handle_s3_optimize
            )
        ]
        
        for tool in tools:
            self.register_tool(tool)

    def register_ai_tools(self, nlp_processor: NLPProcessor) -> None:
        """Register AI-powered tools."""
        tools = [
            MCPTool(
                name="awdx_ai_ask",
                description="Ask questions in natural language about AWS resources",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language query"
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context for the query"
                        }
                    },
                    "required": ["query"]
                },
                handler=lambda args: self._handle_ai_ask(args, nlp_processor)
            ),
            MCPTool(
                name="awdx_ai_explain",
                description="Get AI-powered explanations of AWS configurations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "resource": {
                            "type": "string",
                            "description": "AWS resource to explain"
                        },
                        "detail_level": {
                            "type": "string",
                            "enum": ["basic", "detailed", "technical"],
                            "description": "Level of detail in explanation"
                        }
                    },
                    "required": ["resource"]
                },
                handler=lambda args: self._handle_ai_explain(args, nlp_processor)
            )
        ]
        
        for tool in tools:
            self.register_tool(tool)

    def register_phase3_tools(self) -> None:
        """Register Phase 3 infrastructure automation tools."""
        tools = [
            # Infrastructure Automation
            MCPTool(
                name="awdx_infra_audit",
                description="Audit infrastructure security and compliance",
                input_schema={
                    "type": "object",
                    "properties": {
                        "templates": {
                            "type": "boolean",
                            "description": "Audit CloudFormation/CDK templates"
                        },
                        "security": {
                            "type": "boolean",
                            "description": "Audit infrastructure security configurations"
                        },
                        "compliance": {
                            "type": "boolean",
                            "description": "Check compliance with infrastructure standards"
                        }
                    }
                },
                handler=self._handle_infra_audit
            ),
            MCPTool(
                name="awdx_infra_drift",
                description="Detect and remediate infrastructure drift",
                input_schema={
                    "type": "object",
                    "properties": {
                        "detect": {
                            "type": "boolean",
                            "description": "Detect infrastructure drift"
                        },
                        "remediate": {
                            "type": "boolean",
                            "description": "Remediate detected drift"
                        },
                        "report": {
                            "type": "boolean",
                            "description": "Generate drift report"
                        }
                    }
                },
                handler=self._handle_infra_drift
            ),
            MCPTool(
                name="awdx_template_validate",
                description="Validate CloudFormation/CDK templates",
                input_schema={
                    "type": "object",
                    "properties": {
                        "security": {
                            "type": "boolean",
                            "description": "Validate template security configurations"
                        },
                        "best_practices": {
                            "type": "boolean",
                            "description": "Check against AWS best practices"
                        },
                        "template_path": {
                            "type": "string",
                            "description": "Path to specific template file"
                        }
                    }
                },
                handler=self._handle_template_validate
            ),
            # Container Security
            MCPTool(
                name="awdx_container_scan",
                description="Scan container images for vulnerabilities",
                input_schema={
                    "type": "object",
                    "properties": {
                        "images": {
                            "type": "boolean",
                            "description": "Scan container images for vulnerabilities"
                        },
                        "vulnerabilities": {
                            "type": "boolean",
                            "description": "Scan for security vulnerabilities"
                        },
                        "compliance": {
                            "type": "boolean",
                            "description": "Check compliance with container security standards"
                        }
                    }
                },
                handler=self._handle_container_scan
            ),
            MCPTool(
                name="awdx_container_audit",
                description="Audit container security and configurations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "security": {
                            "type": "boolean",
                            "description": "Audit container security configurations"
                        },
                        "permissions": {
                            "type": "boolean",
                            "description": "Audit container permissions and IAM roles"
                        },
                        "networking": {
                            "type": "boolean",
                            "description": "Audit container networking configurations"
                        }
                    }
                },
                handler=self._handle_container_audit
            ),
            MCPTool(
                name="awdx_k8s_audit",
                description="Audit Kubernetes security and RBAC",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pods": {
                            "type": "boolean",
                            "description": "Audit Kubernetes pods and containers"
                        },
                        "services": {
                            "type": "boolean",
                            "description": "Audit Kubernetes services and networking"
                        },
                        "rbac": {
                            "type": "boolean",
                            "description": "Audit RBAC policies and permissions"
                        },
                        "network_policies": {
                            "type": "boolean",
                            "description": "Audit network policies"
                        }
                    }
                },
                handler=self._handle_k8s_audit
            ),
            # CI/CD Pipeline Security
            MCPTool(
                name="awdx_pipeline_audit",
                description="Audit CI/CD pipelines for security and compliance",
                input_schema={
                    "type": "object",
                    "properties": {
                        "comprehensive": {
                            "type": "boolean",
                            "description": "Run comprehensive pipeline audit"
                        },
                        "fix_issues": {
                            "type": "boolean",
                            "description": "Automatically fix detected issues"
                        }
                    }
                },
                handler=self._handle_pipeline_audit
            ),
            MCPTool(
                name="awdx_build_security",
                description="Scan build processes for security vulnerabilities",
                input_schema={
                    "type": "object",
                    "properties": {
                        "scan": {
                            "type": "boolean",
                            "description": "Scan build configurations for security issues"
                        },
                        "vulnerabilities": {
                            "type": "boolean",
                            "description": "Scan for vulnerabilities in build artifacts"
                        },
                        "auto_fix": {
                            "type": "boolean",
                            "description": "Automatically fix security issues"
                        }
                    }
                },
                handler=self._handle_build_security
            ),
            # Monitoring and Alerting
            MCPTool(
                name="awdx_monitoring_setup",
                description="Setup comprehensive monitoring with best practices",
                input_schema={
                    "type": "object",
                    "properties": {
                        "auto": {
                            "type": "boolean",
                            "description": "Automatically setup monitoring with best practices"
                        },
                        "best_practices": {
                            "type": "boolean",
                            "description": "Apply monitoring best practices"
                        },
                        "alerts": {
                            "type": "boolean",
                            "description": "Setup automated alerts and notifications"
                        }
                    }
                },
                handler=self._handle_monitoring_setup
            ),
            MCPTool(
                name="awdx_alert_configure",
                description="Configure intelligent alerts with automated thresholds",
                input_schema={
                    "type": "object",
                    "properties": {
                        "auto": {
                            "type": "boolean",
                            "description": "Automatically configure alerts with best practices"
                        },
                        "thresholds": {
                            "type": "boolean",
                            "description": "Configure intelligent alert thresholds"
                        },
                        "escalation": {
                            "type": "boolean",
                            "description": "Setup alert escalation policies"
                        }
                    }
                },
                handler=self._handle_alert_configure
            ),
            # Network Security
            MCPTool(
                name="awdx_network_audit",
                description="Audit network configurations and security",
                input_schema={
                    "type": "object",
                    "properties": {
                        "vpc": {
                            "type": "boolean",
                            "description": "Audit VPC configurations and architecture"
                        },
                        "subnets": {
                            "type": "boolean",
                            "description": "Audit subnet configurations and routing"
                        },
                        "security_groups": {
                            "type": "boolean",
                            "description": "Audit security group rules"
                        },
                        "nacls": {
                            "type": "boolean",
                            "description": "Audit Network ACL configurations"
                        }
                    }
                },
                handler=self._handle_network_audit
            ),
            MCPTool(
                name="awdx_sg_audit",
                description="Audit security group rules and compliance",
                input_schema={
                    "type": "object",
                    "properties": {
                        "rules": {
                            "type": "boolean",
                            "description": "Audit security group rules"
                        },
                        "compliance": {
                            "type": "boolean",
                            "description": "Check compliance with security standards"
                        },
                        "best_practices": {
                            "type": "boolean",
                            "description": "Check against security best practices"
                        }
                    }
                },
                handler=self._handle_sg_audit
            ),
            MCPTool(
                name="awdx_sg_optimize",
                description="Optimize security group rules and configurations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "rules": {
                            "type": "boolean",
                            "description": "Optimize security group rules"
                        },
                        "coverage": {
                            "type": "boolean",
                            "description": "Optimize security coverage"
                        },
                        "security": {
                            "type": "boolean",
                            "description": "Optimize security configurations"
                        },
                        "auto_fix": {
                            "type": "boolean",
                            "description": "Automatically apply optimizations"
                        }
                    }
                },
                handler=self._handle_sg_optimize
            )
        ]
        
        for tool in tools:
            self.register_tool(tool)

    # Tool handlers
    async def _handle_profile_list(self, args: Dict[str, Any]) -> str:
        """Handle profile list tool."""
        try:
            # Import and call the profile list function
            from ..profilyze.profile_commands import get_profiles, get_current_profile
            
            profiles = get_profiles()
            current = get_current_profile()
            
            result = {
                "profiles": profiles,
                "current_profile": current,
                "total_profiles": len(profiles)
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error listing profiles: {str(e)}"

    async def _handle_profile_switch(self, args: Dict[str, Any]) -> str:
        """Handle profile switch tool."""
        try:
            profile_name = args["profile_name"]
            from ..profilyze.profile_commands import get_profiles
            
            profiles = get_profiles()
            if profile_name not in profiles:
                return f"Error: Profile '{profile_name}' not found"
            
            return f"To switch to profile '{profile_name}', run: export AWS_PROFILE={profile_name}"
        except Exception as e:
            return f"Error switching profile: {str(e)}"

    async def _handle_profile_add(self, args: Dict[str, Any]) -> str:
        """Handle profile add tool."""
        try:
            profile_name = args["profile_name"]
            access_key = args.get("access_key")
            secret_key = args.get("secret_key")
            region = args.get("region", "us-east-1")
            
            # This would need to be implemented to actually add the profile
            # For now, return instructions
            return f"To add profile '{profile_name}', use: awdx profile add"
        except Exception as e:
            return f"Error adding profile: {str(e)}"

    async def _handle_cost_summary(self, args: Dict[str, Any]) -> str:
        """Handle cost summary tool."""
        try:
            days = args.get("days", 30)
            service = args.get("service")
            profile = args.get("profile")
            
            # For now, return a placeholder response
            result = {
                "message": f"Cost summary for {days} days",
                "command": f"awdx cost summary --days {days}",
                "service": service,
                "profile": profile
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error getting cost summary: {str(e)}"

    async def _handle_cost_trends(self, args: Dict[str, Any]) -> str:
        """Handle cost trends tool."""
        try:
            days = args.get("days", 90)
            granularity = args.get("granularity", "daily")
            
            result = {
                "message": f"Cost trends for {days} days with {granularity} granularity",
                "command": f"awdx cost trends --days {days} --granularity {granularity}"
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error getting cost trends: {str(e)}"

    async def _handle_cost_optimize(self, args: Dict[str, Any]) -> str:
        """Handle cost optimization tool."""
        try:
            threshold = args.get("threshold")
            include_risks = args.get("include_risks", True)
            
            result = {
                "message": "Cost optimization recommendations",
                "command": "awdx cost optimize",
                "threshold": threshold,
                "include_risks": include_risks
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error getting optimization recommendations: {str(e)}"

    async def _handle_iam_audit(self, args: Dict[str, Any]) -> str:
        """Handle IAM audit tool."""
        try:
            checks = args.get("checks")
            output_format = args.get("output_format", "json")
            
            result = {
                "message": "IAM security audit",
                "command": "awdx iam audit",
                "checks": checks,
                "output_format": output_format
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error performing IAM audit: {str(e)}"

    async def _handle_iam_users(self, args: Dict[str, Any]) -> str:
        """Handle IAM users tool."""
        try:
            filters = args.get("filters")
            include_details = args.get("include_details", False)
            
            result = {
                "message": "IAM users list",
                "command": "awdx iam users",
                "filters": filters,
                "include_details": include_details
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error listing IAM users: {str(e)}"

    async def _handle_iam_roles(self, args: Dict[str, Any]) -> str:
        """Handle IAM roles tool."""
        try:
            role_type = args.get("role_type", "all")
            
            result = {
                "message": "IAM roles list",
                "command": "awdx iam roles",
                "role_type": role_type
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error listing IAM roles: {str(e)}"

    async def _handle_s3_audit(self, args: Dict[str, Any]) -> str:
        """Handle S3 audit tool."""
        try:
            bucket_name = args.get("bucket_name")
            checks = args.get("checks")
            
            result = {
                "message": "S3 bucket security audit",
                "command": "awdx s3 audit",
                "bucket_name": bucket_name,
                "checks": checks
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error performing S3 audit: {str(e)}"

    async def _handle_s3_scan(self, args: Dict[str, Any]) -> str:
        """Handle S3 scan tool."""
        try:
            scan_type = args.get("scan_type", "all")
            
            result = {
                "message": "S3 bucket security scan",
                "command": "awdx s3 scan",
                "scan_type": scan_type
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error performing S3 scan: {str(e)}"

    async def _handle_secret_discover(self, args: Dict[str, Any]) -> str:
        """Handle secret discovery tool."""
        try:
            resource_types = args.get("resource_types")
            
            result = {
                "message": "Secret discovery in AWS resources",
                "command": "awdx secret discover",
                "resource_types": resource_types
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error discovering secrets: {str(e)}"

    async def _handle_secret_rotate(self, args: Dict[str, Any]) -> str:
        """Handle secret rotation tool."""
        try:
            secret_type = args.get("secret_type", "all")
            
            result = {
                "message": "Secret rotation",
                "command": "awdx secret rotate",
                "secret_type": secret_type
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error rotating secrets: {str(e)}"

    async def _handle_security_audit(self, args: Dict[str, Any]) -> str:
        """Handle security audit tool."""
        try:
            scope = args.get("scope", "full")
            
            result = {
                "message": "Comprehensive security audit",
                "command": "awdx security audit",
                "scope": scope
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error performing security audit: {str(e)}"

    async def _handle_security_scan(self, args: Dict[str, Any]) -> str:
        """Handle security scan tool."""
        try:
            scan_type = args.get("scan_type", "vulnerability")
            
            result = {
                "message": "Security vulnerability scan",
                "command": "awdx security scan",
                "scan_type": scan_type
            }
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error performing security scan: {str(e)}"

    async def _handle_ai_ask(self, args: Dict[str, Any], nlp_processor: NLPProcessor) -> str:
        """Handle AI ask tool."""
        try:
            query = args["query"]
            context = args.get("context")
            
            result = await nlp_processor.process_query(query, context=context)
            return json.dumps({
                "intent": result.intent.value,
                "confidence": result.confidence,
                "command": result.awdx_command,
                "explanation": result.explanation
            }, indent=2)
        except Exception as e:
            return f"Error processing AI query: {str(e)}"

    async def _handle_ai_explain(self, args: Dict[str, Any], nlp_processor: NLPProcessor) -> str:
        """Handle AI explain tool."""
        try:
            resource = args["resource"]
            detail_level = args.get("detail_level", "basic")
            
            # This would use the AI to explain AWS resources
            explanation = f"AI explanation of {resource} at {detail_level} level"
            return explanation
        except Exception as e:
            return f"Error generating AI explanation: {str(e)}"

    # Phase 2 Tool Handlers
    async def _handle_lambda_audit(self, args: Dict[str, Any]) -> str:
        """Handle Lambda audit command."""
        try:
            security = args.get("security", True)
            permissions = args.get("permissions", True)
            runtime = args.get("runtime", True)
            
            cmd = f"awdx task lambda-audit"
            if not security:
                cmd += " --no-security"
            if not permissions:
                cmd += " --no-permissions"
            if not runtime:
                cmd += " --no-runtime"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running Lambda audit: {str(e)}"

    async def _handle_lambda_optimize(self, args: Dict[str, Any]) -> str:
        """Handle Lambda optimize command."""
        try:
            memory = args.get("memory", True)
            timeout = args.get("timeout", True)
            cold_start = args.get("cold_start", True)
            auto_fix = args.get("auto_fix", False)
            
            cmd = f"awdx task lambda-optimize"
            if not memory:
                cmd += " --no-memory"
            if not timeout:
                cmd += " --no-timeout"
            if not cold_start:
                cmd += " --no-cold-start"
            if auto_fix:
                cmd += " --auto-fix"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running Lambda optimization: {str(e)}"

    async def _handle_lambda_monitor(self, args: Dict[str, Any]) -> str:
        """Handle Lambda monitor command."""
        try:
            performance = args.get("performance", True)
            errors = args.get("errors", True)
            cost = args.get("cost", True)
            continuous = args.get("continuous", False)
            
            cmd = f"awdx task lambda-monitor"
            if not performance:
                cmd += " --no-performance"
            if not errors:
                cmd += " --no-errors"
            if not cost:
                cmd += " --no-cost"
            if continuous:
                cmd += " --continuous"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running Lambda monitoring: {str(e)}"

    async def _handle_iam_audit_comprehensive(self, args: Dict[str, Any]) -> str:
        """Handle comprehensive IAM audit command."""
        try:
            users = args.get("users", True)
            roles = args.get("roles", True)
            policies = args.get("policies", True)
            compliance = args.get("compliance", True)
            
            cmd = f"awdx task iam-audit"
            if not users:
                cmd += " --no-users"
            if not roles:
                cmd += " --no-roles"
            if not policies:
                cmd += " --no-policies"
            if not compliance:
                cmd += " --no-compliance"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running IAM audit: {str(e)}"

    async def _handle_iam_optimize(self, args: Dict[str, Any]) -> str:
        """Handle IAM optimize command."""
        try:
            permissions = args.get("permissions", True)
            least_privilege = args.get("least_privilege", True)
            rotation = args.get("rotation", True)
            auto_fix = args.get("auto_fix", False)
            
            cmd = f"awdx task iam-optimize"
            if not permissions:
                cmd += " --no-permissions"
            if not least_privilege:
                cmd += " --no-least-privilege"
            if not rotation:
                cmd += " --no-rotation"
            if auto_fix:
                cmd += " --auto-fix"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running IAM optimization: {str(e)}"

    async def _handle_s3_audit_comprehensive(self, args: Dict[str, Any]) -> str:
        """Handle comprehensive S3 audit command."""
        try:
            buckets = args.get("buckets", True)
            policies = args.get("policies", True)
            encryption = args.get("encryption", True)
            compliance = args.get("compliance", True)
            
            cmd = f"awdx task s3-audit"
            if not buckets:
                cmd += " --no-buckets"
            if not policies:
                cmd += " --no-policies"
            if not encryption:
                cmd += " --no-encryption"
            if not compliance:
                cmd += " --no-compliance"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running S3 audit: {str(e)}"

    async def _handle_s3_optimize(self, args: Dict[str, Any]) -> str:
        """Handle S3 optimize command."""
        try:
            storage = args.get("storage", True)
            access = args.get("access", True)
            cost = args.get("cost", True)
            auto_fix = args.get("auto_fix", False)
            
            cmd = f"awdx task s3-optimize"
            if not storage:
                cmd += " --no-storage"
            if not access:
                cmd += " --no-access"
            if not cost:
                cmd += " --no-cost"
            if auto_fix:
                cmd += " --auto-fix"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running S3 optimization: {str(e)}"

    # Phase 3 Tool Handlers
    async def _handle_infra_audit(self, args: Dict[str, Any]) -> str:
        """Handle infrastructure audit command."""
        try:
            import subprocess
            templates = args.get("templates", True)
            security = args.get("security", True)
            compliance = args.get("compliance", True)
            
            cmd = "awdx task infra-audit"
            if not templates:
                cmd += " --no-templates"
            if not security:
                cmd += " --no-security"
            if not compliance:
                cmd += " --no-compliance"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running infrastructure audit: {str(e)}"

    async def _handle_infra_drift(self, args: Dict[str, Any]) -> str:
        """Handle infrastructure drift detection command."""
        try:
            import subprocess
            detect = args.get("detect", True)
            remediate = args.get("remediate", False)
            report = args.get("report", True)
            
            cmd = "awdx task infra-drift"
            if not detect:
                cmd += " --no-detect"
            if remediate:
                cmd += " --remediate"
            if not report:
                cmd += " --no-report"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running infrastructure drift detection: {str(e)}"

    async def _handle_template_validate(self, args: Dict[str, Any]) -> str:
        """Handle template validation command."""
        try:
            import subprocess
            security = args.get("security", True)
            best_practices = args.get("best_practices", True)
            template_path = args.get("template_path")
            
            cmd = "awdx task template-validate"
            if not security:
                cmd += " --no-security"
            if not best_practices:
                cmd += " --no-best-practices"
            if template_path:
                cmd += f" --template {template_path}"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running template validation: {str(e)}"

    async def _handle_container_scan(self, args: Dict[str, Any]) -> str:
        """Handle container scan command."""
        try:
            import subprocess
            images = args.get("images", True)
            vulnerabilities = args.get("vulnerabilities", True)
            compliance = args.get("compliance", True)
            
            cmd = "awdx task container-scan"
            if not images:
                cmd += " --no-images"
            if not vulnerabilities:
                cmd += " --no-vulnerabilities"
            if not compliance:
                cmd += " --no-compliance"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running container scan: {str(e)}"

    async def _handle_container_audit(self, args: Dict[str, Any]) -> str:
        """Handle container audit command."""
        try:
            import subprocess
            security = args.get("security", True)
            permissions = args.get("permissions", True)
            networking = args.get("networking", True)
            
            cmd = "awdx task container-audit"
            if not security:
                cmd += " --no-security"
            if not permissions:
                cmd += " --no-permissions"
            if not networking:
                cmd += " --no-networking"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running container audit: {str(e)}"

    async def _handle_k8s_audit(self, args: Dict[str, Any]) -> str:
        """Handle Kubernetes audit command."""
        try:
            import subprocess
            pods = args.get("pods", True)
            services = args.get("services", True)
            rbac = args.get("rbac", True)
            network_policies = args.get("network_policies", True)
            
            cmd = "awdx task k8s-audit"
            if not pods:
                cmd += " --no-pods"
            if not services:
                cmd += " --no-services"
            if not rbac:
                cmd += " --no-rbac"
            if not network_policies:
                cmd += " --no-network-policies"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running Kubernetes audit: {str(e)}"

    async def _handle_pipeline_audit(self, args: Dict[str, Any]) -> str:
        """Handle pipeline audit command."""
        try:
            import subprocess
            comprehensive = args.get("comprehensive", True)
            fix_issues = args.get("fix_issues", False)
            
            cmd = "awdx task pipeline-audit"
            if not comprehensive:
                cmd += " --no-comprehensive"
            if fix_issues:
                cmd += " --fix-issues"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running pipeline audit: {str(e)}"

    async def _handle_build_security(self, args: Dict[str, Any]) -> str:
        """Handle build security scan command."""
        try:
            import subprocess
            scan = args.get("scan", True)
            vulnerabilities = args.get("vulnerabilities", True)
            auto_fix = args.get("auto_fix", False)
            
            cmd = "awdx task build-security"
            if not scan:
                cmd += " --no-scan"
            if not vulnerabilities:
                cmd += " --no-vulnerabilities"
            if auto_fix:
                cmd += " --auto-fix"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running build security scan: {str(e)}"

    async def _handle_monitoring_setup(self, args: Dict[str, Any]) -> str:
        """Handle monitoring setup command."""
        try:
            import subprocess
            auto = args.get("auto", True)
            best_practices = args.get("best_practices", True)
            alerts = args.get("alerts", True)
            
            cmd = "awdx task monitoring-setup"
            if not auto:
                cmd += " --no-auto"
            if not best_practices:
                cmd += " --no-best-practices"
            if not alerts:
                cmd += " --no-alerts"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running monitoring setup: {str(e)}"

    async def _handle_alert_configure(self, args: Dict[str, Any]) -> str:
        """Handle alert configuration command."""
        try:
            import subprocess
            auto = args.get("auto", True)
            thresholds = args.get("thresholds", True)
            escalation = args.get("escalation", True)
            
            cmd = "awdx task alert-configure"
            if not auto:
                cmd += " --no-auto"
            if not thresholds:
                cmd += " --no-thresholds"
            if not escalation:
                cmd += " --no-escalation"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running alert configuration: {str(e)}"

    async def _handle_network_audit(self, args: Dict[str, Any]) -> str:
        """Handle network audit command."""
        try:
            import subprocess
            vpc = args.get("vpc", True)
            subnets = args.get("subnets", True)
            security_groups = args.get("security_groups", True)
            nacls = args.get("nacls", True)
            
            cmd = "awdx task network-audit"
            if not vpc:
                cmd += " --no-vpc"
            if not subnets:
                cmd += " --no-subnets"
            if not security_groups:
                cmd += " --no-security-groups"
            if not nacls:
                cmd += " --no-nacls"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running network audit: {str(e)}"

    async def _handle_sg_audit(self, args: Dict[str, Any]) -> str:
        """Handle security group audit command."""
        try:
            import subprocess
            rules = args.get("rules", True)
            compliance = args.get("compliance", True)
            best_practices = args.get("best_practices", True)
            
            cmd = "awdx task sg-audit"
            if not rules:
                cmd += " --no-rules"
            if not compliance:
                cmd += " --no-compliance"
            if not best_practices:
                cmd += " --no-best-practices"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running security group audit: {str(e)}"

    async def _handle_sg_optimize(self, args: Dict[str, Any]) -> str:
        """Handle security group optimization command."""
        try:
            import subprocess
            rules = args.get("rules", True)
            coverage = args.get("coverage", True)
            security = args.get("security", True)
            auto_fix = args.get("auto_fix", False)
            
            cmd = "awdx task sg-optimize"
            if not rules:
                cmd += " --no-rules"
            if not coverage:
                cmd += " --no-coverage"
            if not security:
                cmd += " --no-security"
            if auto_fix:
                cmd += " --auto-fix"
            
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error running security group optimization: {str(e)}"


# Convenience classes for individual tool types
class ProfileTool:
    """Profile management tool."""
    pass

class CostTool:
    """Cost analysis tool."""
    pass

class IAMTool:
    """IAM security tool."""
    pass

class S3Tool:
    """S3 security tool."""
    pass

class SecretTool:
    """Secret management tool."""
    pass

class SecurityTool:
    """Security assessment tool."""
    pass 