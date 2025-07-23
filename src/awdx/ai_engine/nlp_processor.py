"""
AWDX AI Engine - Natural Language Processor

This module handles natural language processing for AWDX commands including:
- Intent recognition from user queries
- Command mapping to AWDX CLI commands
- Parameter extraction and validation
- Context-aware response generation

Key Features:
    - Natural language to command translation
    - Intent classification and confidence scoring
    - Parameter extraction with type validation
    - Multi-turn conversation support
    - Command suggestions and auto-completion
"""

import json
import logging
import re
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from .exceptions import (
    AuthenticationError,
    CommandMappingError,
    GeminiAPIError,
    IntentRecognitionError,
    NetworkError,
    NLPProcessingError,
    RateLimitError,
    ResponseParsingError,
)
from .gemini_client import GeminiClient

logger = logging.getLogger(__name__)


class Intent(Enum):
    """Supported user intents for AWS DevOps automation."""

    # Profile management intents
    LIST_PROFILES = "list_profiles"
    SWITCH_PROFILE = "switch_profile"
    CREATE_PROFILE = "create_profile"
    DELETE_PROFILE = "delete_profile"
    VALIDATE_PROFILE = "validate_profile"
    GET_CURRENT_PROFILE = "get_current_profile"

    # Cost analysis intents
    SHOW_COSTS = "show_costs"
    COST_TRENDS = "cost_trends"
    COST_OPTIMIZATION = "cost_optimization"
    COST_ALERTS = "cost_alerts"
    BUDGET_MANAGEMENT = "budget_management"
    COST_ANALYSIS = "cost_analysis"
    GET_CURRENT_MONTH_COST = "get_current_month_cost"

    # IAM security intents
    IAM_AUDIT = "iam_audit"
    IAM_USERS = "iam_users"
    IAM_POLICIES = "iam_policies"
    IAM_COMPLIANCE = "iam_compliance"
    IAM_SECURITY_AUDIT = "iam_security_audit"
    LIST_IAM_USERS = "list_iam_users"
    LIST_IAM_ROLES = "list_iam_roles"

    # S3 security intents
    S3_AUDIT = "s3_audit"
    S3_SCAN = "s3_scan"
    S3_COMPLIANCE = "s3_compliance"
    LIST_S3_BUCKETS = "list_s3_buckets"
    S3_SECURITY_SCAN = "s3_security_scan"

    # EC2 management intents
    LIST_EC2_INSTANCES = "list_ec2_instances"
    EC2_SECURITY_GROUPS = "ec2_security_groups"
    EC2_STATUS = "ec2_status"

    # Secret management intents
    SECRET_DISCOVER = "secret_discover"
    SECRET_ROTATE = "secret_rotate"
    SECRET_MONITOR = "secret_monitor"

    # Security assessment intents
    SECURITY_AUDIT = "security_audit"
    VULNERABILITY_SCAN = "vulnerability_scan"
    SECURITY_ASSESSMENT = "security_assessment"
    SECURITY_SCAN = "security_scan"

    # AWS CLI intents
    AWS_CLI_COMMAND = "aws_cli_command"
    AWS_DESCRIBE = "aws_describe"
    AWS_LIST = "aws_list"

    # General intents
    HELP = "help"
    EXPLAIN = "explain"
    SUGGEST = "suggest"
    UNKNOWN = "unknown"


@dataclass
class CommandParameter:
    """Represents a command parameter with validation."""

    name: str
    value: Any
    type: str
    required: bool = False
    description: Optional[str] = None

    def validate(self) -> bool:
        """Validate parameter value against expected type."""
        try:
            if self.type == "string":
                return isinstance(self.value, str)
            elif self.type == "integer":
                return isinstance(self.value, int) or (
                    isinstance(self.value, str) and self.value.isdigit()
                )
            elif self.type == "float":
                return isinstance(self.value, (int, float)) or (
                    isinstance(self.value, str)
                    and re.match(r"^-?\d+(\.\d+)?$", self.value)
                )
            elif self.type == "boolean":
                return isinstance(self.value, bool) or (
                    isinstance(self.value, str)
                    and self.value.lower() in ["true", "false", "yes", "no", "1", "0"]
                )
            elif self.type == "list":
                return isinstance(self.value, list) or (
                    isinstance(self.value, str) and "," in self.value
                )
            return True
        except Exception:
            return False


@dataclass
class ParsedCommand:
    """Represents a parsed natural language command with DevOps intelligence."""

    intent: Intent
    confidence: float
    awdx_command: str
    parameters: List[CommandParameter]
    explanation: str
    suggestions: List[str]
    aws_cli_alternative: Optional[str] = None
    awdx_alternative: Optional[str] = None
    security_considerations: Optional[str] = None
    workflow_context: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "intent": self.intent.value,
            "confidence": self.confidence,
            "awdx_command": self.awdx_command,
            "parameters": [asdict(param) for param in self.parameters],
            "explanation": self.explanation,
            "suggestions": self.suggestions,
            "aws_cli_alternative": self.aws_cli_alternative,
            "awdx_alternative": self.awdx_alternative,
            "security_considerations": self.security_considerations,
            "workflow_context": self.workflow_context,
        }

    def get_full_command(self) -> str:
        """Get the full command with parameters."""
        cmd_parts = [self.awdx_command]

        for param in self.parameters:
            if param.required or param.value is not None:
                if param.type == "boolean" and param.value:
                    cmd_parts.append(f"--{param.name}")
                elif param.type != "boolean":
                    cmd_parts.append(f"--{param.name} {param.value}")

        return " ".join(cmd_parts)

    def get_alternatives(self) -> List[str]:
        """Get list of alternative commands."""
        alternatives = []
        if self.aws_cli_alternative:
            alternatives.append(self.aws_cli_alternative)
        if self.awdx_alternative:
            alternatives.append(self.awdx_alternative)
        return alternatives


class NLPProcessor:
    """
    Processes natural language queries and converts them to AWDX commands.

    This class uses Google Gemini to understand user intent and map natural
    language queries to appropriate AWDX CLI commands with proper parameters.
    """

    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize NLP processor.

        Args:
            gemini_client: Configured Gemini client for AI processing
        """
        self.gemini_client = gemini_client
        self.conversation_history: List[Dict[str, str]] = []

        # Command mapping templates
        self.command_templates = self._load_command_templates()

        # Intent recognition patterns
        self.intent_patterns = self._load_intent_patterns()

    async def process_query(
        self,
        query: str,
        context: Optional[str] = None,
        aws_profile: Optional[str] = None,
    ) -> ParsedCommand:
        """
        Process a natural language query and return parsed command.

        Args:
            query: User's natural language query
            context: Optional conversation context
            aws_profile: Optional AWS profile context

        Returns:
            ParsedCommand: Parsed command with intent and parameters

        Raises:
            NLPProcessingError: If query processing fails
        """
        try:
            logger.info(f"Processing query: {query[:100]}...")

            # Check AWDX capability first
            has_capability, capability_reason = self._check_awdx_capability("", query)

            # Build system prompt for command recognition
            system_prompt = self._build_system_prompt(aws_profile)

            # Add capability context to the prompt
            if not has_capability:
                system_prompt += f"\n\n**IMPORTANT**: {capability_reason}. Prefer AWS CLI for this query."

            # Build context from conversation history
            conversation_context = self._build_conversation_context(context)

            # Generate AI response for intent recognition
            ai_prompt = self._build_intent_recognition_prompt(query)
            full_context = (
                f"{conversation_context}\n\n{ai_prompt}"
                if conversation_context
                else ai_prompt
            )

            response = await self.gemini_client.generate_text(
                prompt=full_context,
                system_prompt=system_prompt,
                temperature=0.2,  # Even lower temperature for more conservative parsing
            )

            # Check if response is valid
            if not response:
                raise NLPProcessingError(
                    "Received empty response from AI model. This might be due to content filtering or rate limits.",
                    user_query=query,
                )

            # Parse AI response into structured command
            parsed_command = self._parse_ai_response(response, query)

            # Add to conversation history
            self.conversation_history.append(
                {
                    "user_query": query,
                    "parsed_command": parsed_command.awdx_command,
                    "intent": parsed_command.intent.value,
                }
            )

            # Keep conversation history limited
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

            logger.info(
                f"Parsed intent: {parsed_command.intent.value} "
                f"(confidence: {parsed_command.confidence:.2f})"
            )

            return parsed_command

        except Exception as e:
            logger.error(f"Query processing failed: {e}")

            # Preserve certain exception types that have specific user-friendly handling
            if isinstance(
                e, (NLPProcessingError, IntentRecognitionError, CommandMappingError)
            ):
                # These are already properly typed NLP exceptions
                raise
            elif isinstance(e, (RateLimitError, AuthenticationError, NetworkError)):
                # These should be handled specifically, don't wrap them
                raise
            elif isinstance(e, GeminiAPIError):
                # Other Gemini API errors should also be preserved
                raise
            else:
                # Only wrap truly unexpected errors
                raise NLPProcessingError(
                    f"Query processing failed: {str(e)}", user_query=query
                )

    def _build_system_prompt(self, aws_profile: Optional[str] = None) -> str:
        """Build system prompt for AI command recognition."""
        return f"""You are an intelligent AWS DevSecOps assistant. You must be ACCURATE about command capabilities.

**CRITICAL: DO NOT INVENT COMMAND PARAMETERS THAT DON'T EXIST**

**AWDX Real Capabilities:**

**awdx profile**: list, switch, add, remove, current, info, validate
- Options: --profile, --help

**awdx cost**: summary, trends, alerts, optimize, export, budget, anomaly, forecast, compare, tags, savings  
- Options: --profile, --region, --output, --start-date, --end-date

**awdx iam**: users, roles, policies, groups, audit, access, compliance, smart, export
- Options: --profile, --region, --output, --include-unused, --risk-threshold

**awdx s3**: audit, scan, compliance, remediate, recommend, monitor, export
- scan options: --profile, --region, --bucket, --type [all|public|encryption|versioning|logging], --output, --include-sensitive
- audit options: --profile, --region, --bucket, --output, --include-objects, --risk-threshold
- ⚠️ **NO SIZE SORTING/ANALYSIS CAPABILITIES** - Use AWS CLI for size queries

**awdx secret**: discover, rotate, monitor, audit, export
**awdx security**: scan, audit, compliance, monitor, export

**AWS CLI for capabilities AWDX lacks:**
- **S3 size analysis**: `aws s3 ls --recursive --summarize | sort -k3 -nr`
- **EC2 detailed listing**: `aws ec2 describe-instances --region us-east-1`
- **Cost by service**: `aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-31 --granularity MONTHLY --metrics BlendedCost --group-by Type,Dimension --group-by Key,SERVICE`

**Decision Rules:**
1. **Size/Storage queries**: Use AWS CLI (AWDX can't sort by size)
2. **Detailed resource listing**: Use AWS CLI (more comprehensive)
3. **Security audits**: Prefer AWDX (specialized for DevSecOps)
4. **Quick checks**: Prefer AWDX (user-friendly output)

**Current Context:**
- AWS Profile: {aws_profile or 'default'}
- Environment: {"Production" if aws_profile and "prod" in aws_profile.lower() else "Development"}

**Response Format:**
{{
    "intent": "specific_intent_name",
    "confidence": 0.95,
    "awdx_command": "primary command (AWDX or AWS CLI)",
    "aws_cli_alternative": "aws cli equivalent if AWDX command was suggested",
    "awdx_alternative": "awdx equivalent if AWS CLI command was suggested", 
    "parameters": [
        {{"name": "param_name", "value": "param_value", "type": "string", "required": false}}
    ],
    "explanation": "Clear explanation focusing on why this tool was chosen",
    "security_considerations": "Security implications",
    "suggestions": ["Related commands", "Follow-up actions"],
    "workflow_context": "DevOps workflow context"
}}

**Intent Values:**
- Profile: list_profiles, get_current_profile, switch_profile
- Cost: show_costs, cost_analysis, get_current_month_cost
- IAM: iam_audit, iam_security_audit, list_iam_users, list_iam_roles
- S3: s3_audit, s3_scan, list_s3_buckets, s3_security_scan
- EC2: list_ec2_instances, ec2_security_groups, ec2_status
- Security: security_audit, security_scan, vulnerability_scan
- AWS CLI: aws_cli_command, aws_describe, aws_list

**BE CONSERVATIVE**: Only suggest parameters that actually exist. When in doubt, use AWS CLI."""

    def _build_conversation_context(
        self, additional_context: Optional[str] = None
    ) -> str:
        """Build conversation context from history."""
        context_parts = []

        if additional_context:
            context_parts.append(f"Additional Context: {additional_context}")

        if self.conversation_history:
            context_parts.append("Recent conversation:")
            for entry in self.conversation_history[-3:]:  # Last 3 interactions
                context_parts.append(f"User: {entry['user_query']}")
                context_parts.append(f"Command: {entry['parsed_command']}")

        return "\n".join(context_parts) if context_parts else ""

    def _build_intent_recognition_prompt(self, query: str) -> str:
        """Build the main prompt for intent recognition."""
        return f"""Please analyze this user query and convert it to an AWDX command:

User Query: "{query}"

Provide a structured JSON response with the intent, command, parameters, and explanation.

Common query patterns and their mappings:

Profile Management:
- "list my aws profiles" → awdx profile list
- "switch to production profile" → awdx profile switch production
- "create new profile" → awdx profile add

Cost Analysis:
- "show my aws costs" → awdx cost summary
- "cost trends for last 90 days" → awdx cost trends --days 90
- "find cost optimization opportunities" → awdx cost optimize

IAM Security:
- "audit iam security" → awdx iam audit
- "check iam compliance" → awdx iam compliance
- "list iam users without mfa" → awdx iam users --no-mfa

S3 Security:
- "scan s3 buckets for security issues" → awdx s3 audit
- "find public s3 buckets" → awdx s3 scan --type public

Secret Management:
- "discover secrets in aws" → awdx secret discover
- "rotate database passwords" → awdx secret rotate --type database

Security Assessment:
- "run security audit" → awdx security audit
- "scan for vulnerabilities" → awdx security scan

Analyze the user's query and provide the appropriate AWDX command mapping."""

    def _parse_ai_response(self, response: str, original_query: str) -> ParsedCommand:
        """Parse AI response into structured ParsedCommand."""
        try:
            # Check if response is valid
            if not response:
                raise ResponseParsingError(
                    "Response is None or empty", response=response
                )

            if not isinstance(response, str):
                raise ResponseParsingError(
                    f"Response is not a string: {type(response)}",
                    response=str(response),
                )

            # Extract JSON from response
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if not json_match:
                raise ResponseParsingError(
                    "No JSON found in AI response", response=response
                )

            json_str = json_match.group(0)
            data = json.loads(json_str)

            # Validate required fields
            required_fields = ["intent", "confidence", "awdx_command", "explanation"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ResponseParsingError(f"Missing required fields: {missing_fields}")

            # Parse intent
            try:
                intent = self._map_intent(data["intent"])
            except ValueError:
                logger.warning(f"Unknown intent: {data['intent']}, using UNKNOWN")
                intent = Intent.UNKNOWN

            # Parse parameters
            parameters = []
            for param_data in data.get("parameters", []):
                param = CommandParameter(
                    name=param_data.get("name", ""),
                    value=param_data.get("value"),
                    type=param_data.get("type", "string"),
                    required=param_data.get("required", False),
                    description=param_data.get("description"),
                )

                if param.validate():
                    parameters.append(param)
                else:
                    logger.warning(f"Invalid parameter: {param.name}={param.value}")

            # Create parsed command
            parsed_command = ParsedCommand(
                intent=intent,
                confidence=min(max(float(data["confidence"]), 0.0), 1.0),
                awdx_command=(data["awdx_command"] or "").strip(),
                parameters=parameters,
                explanation=(data["explanation"] or "").strip(),
                suggestions=data.get("suggestions", []),
                aws_cli_alternative=data.get("aws_cli_alternative"),
                awdx_alternative=data.get("awdx_alternative"),
                security_considerations=data.get("security_considerations"),
                workflow_context=data.get("workflow_context"),
            )

            # Validate command format
            if not self._validate_awdx_command(parsed_command.awdx_command):
                logger.warning(
                    f"Invalid AWDX command format: {parsed_command.awdx_command}"
                )

                # If it's an AWDX command with invalid parameters, suggest AWS CLI
                if parsed_command.awdx_command.startswith("awdx "):
                    parsed_command.confidence *= 0.3  # Severely reduce confidence
                    parsed_command.explanation += " **Note**: Some suggested parameters may not exist in AWDX. Consider using AWS CLI alternative."

                    # Add AWS CLI suggestion if not already present
                    if not parsed_command.aws_cli_alternative:
                        parsed_command.aws_cli_alternative = (
                            self._suggest_aws_cli_alternative(
                                query, parsed_command.awdx_command
                            )
                        )
                else:
                    parsed_command.confidence *= (
                        0.7  # Reduce confidence for other invalid commands
                    )

            return parsed_command

        except json.JSONDecodeError as e:
            raise ResponseParsingError(
                f"Invalid JSON in AI response: {str(e)}", response=response
            )
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")

            # Fallback to simple command extraction
            return ParsedCommand(
                intent=Intent.UNKNOWN,
                confidence=0.3,
                awdx_command=f"# Could not parse: {original_query}",
                parameters=[],
                explanation="Failed to parse AI response into structured command",
                suggestions=[],
                aws_cli_alternative=None,
                awdx_alternative=None,
                security_considerations=None,
                workflow_context=None,
            )

    def _validate_awdx_command(self, command: str) -> bool:
        """
        Validate AWDX command against actual capabilities.

        Args:
            command: AWDX command to validate

        Returns:
            bool: True if command is valid and supported
        """
        if not command.startswith("awdx "):
            return False

        # Parse command structure
        parts = command.split()
        if len(parts) < 3:  # awdx module subcommand
            return False

        module = f"awdx {parts[1]}"
        subcommand = parts[2]

        # Check if module exists
        if module not in self.command_templates:
            return False

        # Check if subcommand exists
        template = self.command_templates[module]
        if subcommand not in template.get("commands", []):
            return False

        # Validate parameters if present
        if len(parts) > 3:
            return self._validate_command_parameters(command, module, subcommand)

        return True

    def _validate_command_parameters(
        self, command: str, module: str, subcommand: str
    ) -> bool:
        """
        Validate command parameters against known options.

        Args:
            command: Full command string
            module: AWDX module (e.g., "awdx s3")
            subcommand: Subcommand (e.g., "scan")

        Returns:
            bool: True if parameters are valid
        """
        template = self.command_templates[module]

        # Get valid options for this subcommand
        valid_options = template.get("common_options", [])
        subcommand_options = template.get(f"{subcommand}_options", [])
        valid_options.extend(subcommand_options)

        # Parse command parameters
        parts = command.split()
        for i, part in enumerate(parts):
            if part.startswith("--"):
                option = part.split("=")[0]  # Handle --option=value format
                if option not in valid_options:
                    logger.warning(
                        f"Invalid option '{option}' for {module} {subcommand}"
                    )
                    return False

        return True

    def _check_awdx_capability(self, intent: str, query: str) -> tuple[bool, str]:
        """
        Check if AWDX has the capability to handle a specific intent.

        Args:
            intent: User intent
            query: Original query

        Returns:
            tuple: (has_capability, reason_if_not)
        """
        # Check for size-related queries with S3
        if "s3" in query.lower() and any(
            word in query.lower() for word in ["size", "biggest", "largest", "storage"]
        ):
            return False, "AWDX S3 commands don't support size analysis or sorting"

        # Check for detailed resource listing
        if (
            any(word in query.lower() for word in ["list all", "show all"])
            and "ec2" in query.lower()
        ):
            return False, "AWDX doesn't have comprehensive EC2 instance listing"

        # Check for region-specific operations
        if "region" in query.lower() and any(
            word in query.lower() for word in ["us-east-1", "us-west-2", "eu-"]
        ):
            for module in ["s3", "cost"]:
                if module in query.lower():
                    return True, f"AWDX {module} supports region filtering"

        return True, "AWDX should handle this"

    def _load_command_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Load real AWDX command templates to prevent hallucination.

        Returns:
            Dict: Mapping of commands to their actual options and capabilities
        """
        return {
            # Profile management commands
            "awdx profile": {
                "commands": [
                    "list",
                    "switch",
                    "add",
                    "remove",
                    "current",
                    "info",
                    "validate",
                ],
                "common_options": ["--profile", "--help"],
                "capabilities": [
                    "list_profiles",
                    "switch_profiles",
                    "manage_credentials",
                ],
            },
            # Cost analysis commands
            "awdx cost": {
                "commands": [
                    "summary",
                    "trends",
                    "alerts",
                    "optimize",
                    "export",
                    "budget",
                    "anomaly",
                    "forecast",
                    "compare",
                    "tags",
                    "savings",
                ],
                "common_options": ["--profile", "--region", "--output", "--help"],
                "summary_options": [
                    "--profile",
                    "--region",
                    "--start-date",
                    "--end-date",
                    "--output",
                ],
                "capabilities": [
                    "cost_analysis",
                    "trends",
                    "optimization",
                    "budgeting",
                ],
            },
            # IAM security commands
            "awdx iam": {
                "commands": [
                    "users",
                    "roles",
                    "policies",
                    "groups",
                    "audit",
                    "access",
                    "compliance",
                    "smart",
                    "export",
                ],
                "common_options": ["--profile", "--region", "--output", "--help"],
                "audit_options": [
                    "--profile",
                    "--region",
                    "--output",
                    "--include-unused",
                    "--risk-threshold",
                ],
                "capabilities": [
                    "security_audit",
                    "compliance_check",
                    "user_management",
                ],
            },
            # S3 security commands
            "awdx s3": {
                "commands": [
                    "audit",
                    "scan",
                    "compliance",
                    "remediate",
                    "recommend",
                    "monitor",
                    "export",
                ],
                "common_options": [
                    "--profile",
                    "--region",
                    "--bucket",
                    "--output",
                    "--help",
                ],
                "scan_options": [
                    "--profile",
                    "--region",
                    "--bucket",
                    "--type",
                    "--output",
                    "--include-sensitive",
                ],
                "audit_options": [
                    "--profile",
                    "--region",
                    "--bucket",
                    "--output",
                    "--include-objects",
                    "--risk-threshold",
                ],
                "scan_types": ["all", "public", "encryption", "versioning", "logging"],
                "capabilities": [
                    "security_scan",
                    "compliance_check",
                    "bucket_analysis",
                ],
                "limitations": [
                    "no_size_sorting",
                    "no_size_analysis",
                    "no_storage_metrics",
                ],
            },
            # Secret management commands
            "awdx secret": {
                "commands": ["discover", "rotate", "monitor", "audit", "export"],
                "common_options": ["--profile", "--region", "--output", "--help"],
                "capabilities": ["secret_discovery", "rotation", "monitoring"],
            },
            # Security assessment commands
            "awdx security": {
                "commands": ["scan", "audit", "compliance", "monitor", "export"],
                "common_options": ["--profile", "--region", "--output", "--help"],
                "capabilities": [
                    "comprehensive_security",
                    "vulnerability_scan",
                    "compliance",
                ],
            },
        }

    def _load_intent_patterns(self) -> Dict[Intent, List[str]]:
        """Load regex patterns for intent recognition fallback."""
        return {
            Intent.LIST_PROFILES: [
                r"list.*profile",
                r"show.*profile",
                r"what.*profile",
            ],
            Intent.SWITCH_PROFILE: [
                r"switch.*profile",
                r"change.*profile",
                r"use.*profile",
            ],
            Intent.SHOW_COSTS: [
                r"show.*cost",
                r"cost.*summary",
                r"aws.*cost",
                r"how much.*spend",
            ],
            Intent.IAM_AUDIT: [r"iam.*audit", r"check.*iam", r"iam.*security"],
            Intent.S3_AUDIT: [r"s3.*audit", r"bucket.*security", r"s3.*scan"],
        }

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history.copy()

    def clear_conversation_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")

    def suggest_commands(self, partial_query: str) -> List[str]:
        """Suggest possible commands based on partial query."""
        suggestions = []
        query_lower = partial_query.lower()

        # Basic pattern matching for suggestions
        if "profile" in query_lower:
            suggestions.extend(
                [
                    "awdx profile list",
                    "awdx profile switch <profile-name>",
                    "awdx profile add",
                ]
            )

        if "cost" in query_lower:
            suggestions.extend(
                [
                    "awdx cost summary",
                    "awdx cost trends --days 90",
                    "awdx cost optimize",
                ]
            )

        if "iam" in query_lower:
            suggestions.extend(
                ["awdx iam audit", "awdx iam users", "awdx iam compliance"]
            )

        if "s3" in query_lower or "bucket" in query_lower:
            suggestions.extend(
                ["awdx s3 audit", "awdx s3 scan --type public", "awdx s3 compliance"]
            )

        return suggestions[:5]  # Limit to 5 suggestions

    def _map_intent(self, ai_intent: str) -> Intent:
        """
        Intelligently map AI-generated intent to our Intent enum.

        Args:
            ai_intent: Intent string from AI response

        Returns:
            Intent: Mapped intent enum value
        """
        if not ai_intent:
            return Intent.UNKNOWN

        # Normalize the intent string
        normalized = ai_intent.lower().replace(" ", "_").replace("-", "_")

        # Direct mapping for exact matches
        try:
            return Intent(normalized)
        except ValueError:
            pass

        # Intelligent fuzzy mapping
        intent_mappings = {
            # Profile management
            "list_aws_profiles": Intent.LIST_PROFILES,
            "show_profiles": Intent.LIST_PROFILES,
            "get_profiles": Intent.LIST_PROFILES,
            "current_profile": Intent.GET_CURRENT_PROFILE,
            "get_current_aws_profile": Intent.GET_CURRENT_PROFILE,
            "active_profile": Intent.GET_CURRENT_PROFILE,
            # Cost analysis
            "cost_summary": Intent.SHOW_COSTS,
            "aws_costs": Intent.SHOW_COSTS,
            "billing": Intent.SHOW_COSTS,
            "cost_report": Intent.SHOW_COSTS,
            "spending": Intent.SHOW_COSTS,
            "monthly_cost": Intent.GET_CURRENT_MONTH_COST,
            "current_month_cost": Intent.GET_CURRENT_MONTH_COST,
            "this_month_cost": Intent.GET_CURRENT_MONTH_COST,
            # IAM security
            "iam_security_audit": Intent.IAM_AUDIT,
            "iam_audit": Intent.IAM_AUDIT,
            "audit_iam": Intent.IAM_AUDIT,
            "iam_security": Intent.IAM_AUDIT,
            "list_users": Intent.LIST_IAM_USERS,
            "iam_users": Intent.IAM_USERS,
            "list_roles": Intent.LIST_IAM_ROLES,
            # S3 security
            "s3_security_scan": Intent.S3_SCAN,
            "scan_s3_buckets": Intent.S3_SCAN,
            "s3_security": Intent.S3_AUDIT,
            "list_buckets": Intent.LIST_S3_BUCKETS,
            "s3_buckets": Intent.LIST_S3_BUCKETS,
            # EC2 management
            "list_instances": Intent.LIST_EC2_INSTANCES,
            "ec2_instances": Intent.LIST_EC2_INSTANCES,
            "show_instances": Intent.LIST_EC2_INSTANCES,
            "instances": Intent.LIST_EC2_INSTANCES,
            # Security
            "security_audit": Intent.SECURITY_AUDIT,
            "security_scan": Intent.SECURITY_SCAN,
            "vulnerability_scan": Intent.VULNERABILITY_SCAN,
            "security_assessment": Intent.SECURITY_ASSESSMENT,
            "aws_security": Intent.SECURITY_AUDIT,
            # AWS CLI
            "aws_command": Intent.AWS_CLI_COMMAND,
            "aws_cli": Intent.AWS_CLI_COMMAND,
            "describe": Intent.AWS_DESCRIBE,
            "list": Intent.AWS_LIST,
        }

        # Check fuzzy mappings
        for pattern, intent in intent_mappings.items():
            if pattern in normalized or normalized in pattern:
                return intent

        # Check for keywords in intent
        if any(keyword in normalized for keyword in ["cost", "billing", "spend"]):
            return Intent.COST_ANALYSIS
        elif any(
            keyword in normalized for keyword in ["iam", "user", "role", "policy"]
        ):
            return Intent.IAM_AUDIT
        elif any(keyword in normalized for keyword in ["s3", "bucket"]):
            return Intent.S3_AUDIT
        elif any(keyword in normalized for keyword in ["security", "audit", "scan"]):
            return Intent.SECURITY_AUDIT
        elif any(keyword in normalized for keyword in ["profile", "credential"]):
            return Intent.LIST_PROFILES
        elif any(keyword in normalized for keyword in ["ec2", "instance"]):
            return Intent.LIST_EC2_INSTANCES

        return Intent.UNKNOWN

    def _suggest_aws_cli_alternative(self, query: str, invalid_command: str) -> str:
        """
        Suggest AWS CLI alternative for invalid AWDX commands.

        Args:
            query: Original user query
            invalid_command: Invalid AWDX command

        Returns:
            str: Suggested AWS CLI command
        """
        query_lower = query.lower()

        # S3 size-related queries
        if "s3" in query_lower and any(
            word in query_lower for word in ["size", "biggest", "largest"]
        ):
            return "aws s3 ls --recursive --summarize | awk '{print $4, $5}' | sort -hr | head -n 1"

        # S3 general listing
        if "s3" in query_lower and any(
            word in query_lower for word in ["list", "show", "buckets"]
        ):
            return "aws s3 ls"

        # EC2 listing
        if "ec2" in query_lower:
            return "aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,State.Name,Tags[?Key==`Name`].Value|[0]]' --output table"

        # IAM listing
        if "iam" in query_lower and "users" in query_lower:
            return "aws iam list-users --query 'Users[*].[UserName,CreateDate]' --output table"

        # Cost analysis
        if "cost" in query_lower:
            return "aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-31 --granularity MONTHLY --metrics BlendedCost"

        # Default suggestion
        return "aws --help"
