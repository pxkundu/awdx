"""
AWDX AI Engine Configuration Manager

This module handles all configuration aspects for the AI engine including:
- Loading configuration from files and environment variables
- Validating configuration settings
- Managing security settings and API keys
- Providing defaults and schema validation

Configuration Sources (in priority order):
1. Environment variables (highest priority)
2. User config file (~/.awdx/ai_config.yaml)
3. Project config file (./awdx.ai.yaml)
4. Default settings (lowest priority)
"""

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Supported logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class OutputFormat(Enum):
    """Supported output formats."""

    TABLE = "table"
    JSON = "json"
    YAML = "yaml"
    CSV = "csv"


@dataclass
class GeminiConfig:
    """Configuration for Google Gemini API."""

    # API configuration
    api_key: Optional[str] = None
    model: str = "gemini-1.5-flash"
    max_tokens: int = 1000000
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40

    # Safety settings
    safety_threshold: str = "BLOCK_MEDIUM_AND_ABOVE"

    # Performance settings
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0

    def validate(self) -> None:
        """Validate Gemini configuration."""
        if not self.api_key:
            raise ConfigurationError(
                "Gemini API key is required. Set GEMINI_API_KEY environment variable.",
                config_key="gemini.api_key",
            )

        if not self.api_key.startswith("AI"):
            raise ConfigurationError(
                "Invalid Gemini API key format. Key should start with 'AI'.",
                config_key="gemini.api_key",
            )

        if not 0.0 <= self.temperature <= 1.0:
            raise ConfigurationError(
                f"Temperature must be between 0.0 and 1.0, got {self.temperature}",
                config_key="gemini.temperature",
            )

        if not 0.0 <= self.top_p <= 1.0:
            raise ConfigurationError(
                f"Top-p must be between 0.0 and 1.0, got {self.top_p}",
                config_key="gemini.top_p",
            )

        if self.max_tokens <= 0:
            raise ConfigurationError(
                f"Max tokens must be positive, got {self.max_tokens}",
                config_key="gemini.max_tokens",
            )


@dataclass
class FeatureFlags:
    """Feature flags for enabling/disabling AI capabilities."""

    natural_language: bool = True
    multimodal: bool = True
    conversation_mode: bool = True
    workflow_automation: bool = True
    predictive_analytics: bool = False  # Beta feature
    learning: bool = True
    caching: bool = True

    def validate(self) -> None:
        """Validate feature flags."""
        # No specific validation needed for boolean flags
        pass


@dataclass
class SecurityConfig:
    """Security configuration for AI engine."""

    # Data handling
    encrypt_context: bool = True
    mask_sensitive_data: bool = True
    log_interactions: bool = False

    # Access control
    allowed_domains: List[str] = field(
        default_factory=lambda: [
            "*.amazonaws.com",
            "ai.google.dev",
            "gemini.google.com",
        ]
    )

    # Privacy settings
    anonymous_usage_data: bool = False
    telemetry_enabled: bool = False

    def validate(self) -> None:
        """Validate security configuration."""
        if self.log_interactions and not self.mask_sensitive_data:
            logger.warning(
                "Logging interactions without masking sensitive data. "
                "Consider enabling mask_sensitive_data for better security."
            )


@dataclass
class PerformanceConfig:
    """Performance configuration for AI engine."""

    # Concurrency
    max_concurrent_requests: int = 5

    # Caching
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds
    max_cache_size: int = 1000  # number of entries

    # Rate limiting
    rate_limit: int = 60  # requests per minute
    burst_limit: int = 10  # requests in burst

    # Context management
    max_context_size: int = 500000  # tokens
    context_compression: bool = True

    def validate(self) -> None:
        """Validate performance configuration."""
        if self.max_concurrent_requests <= 0:
            raise ConfigurationError(
                f"Max concurrent requests must be positive, got {self.max_concurrent_requests}",
                config_key="performance.max_concurrent_requests",
            )

        if self.rate_limit <= 0:
            raise ConfigurationError(
                f"Rate limit must be positive, got {self.rate_limit}",
                config_key="performance.rate_limit",
            )

        if self.max_context_size <= 0:
            raise ConfigurationError(
                f"Max context size must be positive, got {self.max_context_size}",
                config_key="performance.max_context_size",
            )


@dataclass
class PersonalizationConfig:
    """User personalization configuration."""

    expertise_level: str = "intermediate"  # beginner, intermediate, expert
    role: str = "devsecops"  # developer, security, ops, devsecops
    preferred_output: str = "detailed"  # brief, detailed, technical
    learning_enabled: bool = True
    suggestion_frequency: str = "normal"  # minimal, normal, verbose

    def validate(self) -> None:
        """Validate personalization configuration."""
        valid_expertise = ["beginner", "intermediate", "expert"]
        if self.expertise_level not in valid_expertise:
            raise ConfigurationError(
                f"Invalid expertise level '{self.expertise_level}'. "
                f"Must be one of: {', '.join(valid_expertise)}",
                config_key="personalization.expertise_level",
            )

        valid_roles = ["developer", "security", "ops", "devsecops"]
        if self.role not in valid_roles:
            raise ConfigurationError(
                f"Invalid role '{self.role}'. Must be one of: {', '.join(valid_roles)}",
                config_key="personalization.role",
            )

        valid_outputs = ["brief", "detailed", "technical"]
        if self.preferred_output not in valid_outputs:
            raise ConfigurationError(
                f"Invalid preferred output '{self.preferred_output}'. "
                f"Must be one of: {', '.join(valid_outputs)}",
                config_key="personalization.preferred_output",
            )


@dataclass
class AIConfig:
    """Main AI engine configuration class."""

    # Core configuration sections
    gemini: GeminiConfig = field(default_factory=GeminiConfig)
    features: FeatureFlags = field(default_factory=FeatureFlags)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    personalization: PersonalizationConfig = field(
        default_factory=PersonalizationConfig
    )

    # Global settings
    enabled: bool = True
    log_level: LogLevel = LogLevel.INFO
    debug_mode: bool = False
    default_output_format: OutputFormat = OutputFormat.TABLE

    # Configuration metadata
    version: str = "1.0.0"
    config_file_path: Optional[str] = None

    def validate(self) -> None:
        """Validate the entire configuration."""
        try:
            logger.info("Validating AI engine configuration...")

            # Validate each section
            self.gemini.validate()
            self.features.validate()
            self.security.validate()
            self.performance.validate()
            self.personalization.validate()

            # Cross-section validation
            if self.features.multimodal and not self.gemini.api_key:
                raise ConfigurationError(
                    "Multimodal features require a valid Gemini API key"
                )

            if self.features.caching and not self.performance.cache_enabled:
                logger.warning(
                    "Caching feature is enabled but performance.cache_enabled is False"
                )

            logger.info("Configuration validation completed successfully")

        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            else:
                raise ConfigurationError(f"Configuration validation failed: {str(e)}")

    def is_enabled(self) -> bool:
        """Check if AI engine is enabled."""
        return self.enabled and self.gemini.api_key is not None

    def has_valid_api_key(self) -> bool:
        """Check if a valid API key is configured."""
        return (
            self.gemini.api_key is not None
            and len(self.gemini.api_key.strip()) > 0
            and self.gemini.api_key.startswith("AI")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        config_dict: Dict[str, Any] = asdict(self)

        # Mask sensitive data if enabled
        if self.security.mask_sensitive_data and config_dict.get("gemini", {}).get(
            "api_key"
        ):
            config_dict["gemini"]["api_key"] = "***MASKED***"

        return config_dict

    def to_yaml(self) -> str:
        """Convert configuration to YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False, indent=2)

    def to_json(self) -> str:
        """Convert configuration to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "AIConfig":
        """Create configuration from dictionary."""
        try:
            # Extract nested configurations
            gemini_config = GeminiConfig(**config_dict.get("gemini", {}))
            features_config = FeatureFlags(**config_dict.get("features", {}))
            security_config = SecurityConfig(**config_dict.get("security", {}))
            performance_config = PerformanceConfig(**config_dict.get("performance", {}))
            personalization_config = PersonalizationConfig(
                **config_dict.get("personalization", {})
            )

            # Convert enum values
            log_level = config_dict.get("log_level", "INFO")
            if isinstance(log_level, str):
                log_level = LogLevel(log_level)

            output_format = config_dict.get("default_output_format", "table")
            if isinstance(output_format, str):
                output_format = OutputFormat(output_format)

            # Create main config
            config = cls(
                gemini=gemini_config,
                features=features_config,
                security=security_config,
                performance=performance_config,
                personalization=personalization_config,
                enabled=config_dict.get("enabled", True),
                log_level=log_level,
                debug_mode=config_dict.get("debug_mode", False),
                default_output_format=output_format,
                version=config_dict.get("version", "1.0.0"),
            )

            return config

        except Exception as e:
            raise ConfigurationError(
                f"Failed to create configuration from dictionary: {str(e)}"
            )

    @classmethod
    def load_from_file(cls, file_path: Optional[str] = None) -> "AIConfig":
        """
        Load configuration from file.

        Args:
            file_path: Optional path to configuration file. If None, will search
                      for default configuration files.

        Returns:
            AIConfig: Loaded configuration

        Raises:
            ConfigurationError: If file cannot be loaded or parsed
        """
        if file_path is None:
            file_path = cls._find_config_file()

        if file_path is None or not Path(file_path).exists():
            logger.info(
                "No configuration file found, using defaults with environment variables"
            )
            return cls.load_default()

        try:
            with open(file_path, "r") as f:
                if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                    config_dict = yaml.safe_load(f)
                elif file_path.endswith(".json"):
                    config_dict = json.load(f)
                else:
                    raise ConfigurationError(
                        f"Unsupported configuration file format: {file_path}"
                    )

            config = cls.from_dict(config_dict or {})
            config.config_file_path = file_path

            # Override with environment variables
            config._apply_environment_overrides()

            logger.info(f"Configuration loaded from {file_path}")
            return config

        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            else:
                raise ConfigurationError(
                    f"Failed to load configuration from {file_path}: {str(e)}"
                )

    @classmethod
    def load_default(cls) -> "AIConfig":
        """
        Load default configuration with environment variable overrides.

        Returns:
            AIConfig: Default configuration with environment overrides
        """
        config = cls()
        config._apply_environment_overrides()

        logger.info("Using default configuration with environment variable overrides")
        return config

    def _apply_environment_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        # Gemini API key (most important)
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.gemini.api_key = api_key

        # Other Gemini settings
        model = os.getenv("GEMINI_MODEL")
        if model:
            self.gemini.model = model

        temp_value = os.getenv("GEMINI_TEMPERATURE")
        if temp_value:
            try:
                self.gemini.temperature = float(temp_value)
            except ValueError:
                logger.warning("Invalid GEMINI_TEMPERATURE value, using default")

        # Feature flags
        enabled_value = os.getenv("AWDX_AI_ENABLED")
        if enabled_value:
            self.enabled = enabled_value.lower() in [
                "true",
                "1",
                "yes",
                "on",
            ]

        multimodal_value = os.getenv("AWDX_AI_MULTIMODAL")
        if multimodal_value:
            self.features.multimodal = multimodal_value.lower() in [
                "true",
                "1",
                "yes",
                "on",
            ]

        # Performance settings
        rate_limit_value = os.getenv("AWDX_AI_RATE_LIMIT")
        if rate_limit_value:
            try:
                self.performance.rate_limit = int(rate_limit_value)
            except ValueError:
                logger.warning("Invalid AWDX_AI_RATE_LIMIT value, using default")

        # Security settings
        log_interactions_value = os.getenv("AWDX_AI_LOG_INTERACTIONS")
        if log_interactions_value:
            self.security.log_interactions = log_interactions_value.lower() in ["true", "1", "yes", "on"]

        # Debug mode
        debug_value = os.getenv("AWDX_DEBUG")
        if debug_value:
            self.debug_mode = debug_value.lower() in [
                "true",
                "1",
                "yes",
                "on",
            ]

        # Log level
        log_level_value = os.getenv("AWDX_LOG_LEVEL")
        if log_level_value:
            try:
                self.log_level = LogLevel(log_level_value.upper())
            except ValueError:
                logger.warning("Invalid AWDX_LOG_LEVEL value, using default")

    @staticmethod
    def _find_config_file() -> Optional[str]:
        """
        Find configuration file in standard locations.

        Returns:
            Optional[str]: Path to configuration file if found
        """
        # Search paths in priority order
        search_paths = [
            Path.home() / ".awdx" / "ai_config.yaml",
            Path.home() / ".awdx" / "ai_config.yml",
            Path.home() / ".config" / "awdx" / "ai_config.yaml",
            Path.cwd() / "awdx.ai.yaml",
            Path.cwd() / "awdx.ai.yml",
            Path.cwd() / ".awdx" / "ai_config.yaml",
        ]

        for path in search_paths:
            if path.exists():
                return str(path)

        return None

    def save_to_file(self, file_path: Optional[str] = None) -> None:
        """
        Save configuration to file.

        Args:
            file_path: Optional path to save configuration. If None, will use
                      default location.

        Raises:
            ConfigurationError: If file cannot be saved
        """
        if file_path is None:
            # Create default config directory if it doesn't exist
            config_dir = Path.home() / ".awdx"
            config_dir.mkdir(exist_ok=True)
            file_path = config_dir / "ai_config.yaml"

        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w") as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)

            self.config_file_path = str(file_path)
            logger.info(f"Configuration saved to {file_path}")

        except Exception as e:
            raise ConfigurationError(
                f"Failed to save configuration to {file_path}: {str(e)}"
            )

    def get_config_template(self) -> str:
        """
        Get a configuration template with comments.

        Returns:
            str: YAML configuration template with documentation
        """
        template = """# AWDX AI Engine Configuration
# This file configures the AI/NLP capabilities of AWDX

# Global AI engine settings
enabled: true
debug_mode: false
log_level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
default_output_format: table  # table, json, yaml, csv

# Google Gemini API configuration
gemini:
  api_key: null  # Set via GEMINI_API_KEY environment variable
  model: gemini-1.5-flash
  max_tokens: 1000000
  temperature: 0.7  # 0.0 = deterministic, 1.0 = very creative
  top_p: 0.9
  top_k: 40
  timeout: 30
  max_retries: 3
  retry_delay: 1.0

# Feature flags - enable/disable specific AI capabilities
features:
  natural_language: true       # Enable natural language commands
  multimodal: true            # Enable document/image processing
  conversation_mode: true      # Enable chat mode
  workflow_automation: true    # Enable workflow automation
  predictive_analytics: false # Beta: Enable predictive features
  learning: true              # Enable user behavior learning
  caching: true               # Enable response caching

# Security and privacy settings
security:
  encrypt_context: true       # Encrypt conversation context
  mask_sensitive_data: true   # Mask sensitive data in logs
  log_interactions: false     # Log AI interactions (for debugging)
  anonymous_usage_data: false # Share anonymous usage statistics
  telemetry_enabled: false    # Enable telemetry data collection
  allowed_domains:
    - "*.amazonaws.com"
    - "ai.google.dev"
    - "gemini.google.com"

# Performance and resource management
performance:
  max_concurrent_requests: 5  # Maximum concurrent AI requests
  cache_enabled: true         # Enable response caching
  cache_ttl: 3600            # Cache time-to-live in seconds
  max_cache_size: 1000       # Maximum cache entries
  rate_limit: 60             # Requests per minute
  burst_limit: 10            # Burst request limit
  max_context_size: 500000   # Maximum context size in tokens
  context_compression: true   # Enable context compression

# User personalization settings
personalization:
  expertise_level: intermediate  # beginner, intermediate, expert
  role: devsecops               # developer, security, ops, devsecops
  preferred_output: detailed    # brief, detailed, technical
  learning_enabled: true       # Enable personalized learning
  suggestion_frequency: normal # minimal, normal, verbose
"""
        return template
