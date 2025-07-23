"""
AWDX AI Engine - Natural Language Processing for AWS DevSecOps

This module provides AI/NLP capabilities for AWDX, enabling natural language
interaction with AWS DevSecOps tools through Google Gemini integration.

Key Components:
    - GeminiClient: Core AI client for Gemini API integration
    - NLPProcessor: Natural language processing and intent recognition
    - ContextManager: Conversation context and session management
    - ResponseFormatter: Format AI responses for CLI output
    - ConfigManager: AI engine configuration management

Version: 1.0.0
Author: AWDX Team
License: MIT
"""

import logging
from typing import Optional

# Package version
__version__ = "1.0.0"

# Setup module-level logger
logger = logging.getLogger(__name__)

# Core AI engine components (lazy imports to avoid circular dependencies)
from .config_manager import AIConfig
from .exceptions import (
    AIEngineError,
    ConfigurationError,
    ContextError,
    GeminiAPIError,
    NLPProcessingError,
)

# Public API exports
__all__ = [
    "AIConfig",
    "AIEngineError",
    "GeminiAPIError",
    "NLPProcessingError",
    "ContextError",
    "ConfigurationError",
    "__version__",
]


def get_ai_client(config: Optional[AIConfig] = None):
    """
    Factory function to get a configured AI client instance.

    Args:
        config: Optional AI configuration. If None, will load from default config.

    Returns:
        GeminiClient: Configured Gemini client instance

    Raises:
        ConfigurationError: If configuration is invalid
        GeminiAPIError: If API client initialization fails
    """
    from .gemini_client import GeminiClient

    if config is None:
        config = AIConfig.load_default()

    return GeminiClient(config)


def get_nlp_processor(ai_client=None, config: Optional[AIConfig] = None):
    """
    Factory function to get a configured NLP processor instance.

    Args:
        ai_client: Optional pre-configured AI client
        config: Optional AI configuration

    Returns:
        NLPProcessor: Configured NLP processor instance
    """
    from .nlp_processor import NLPProcessor

    if ai_client is None:
        ai_client = get_ai_client(config)

    return NLPProcessor(ai_client)


def initialize_ai_engine(config_path: Optional[str] = None) -> bool:
    """
    Initialize the AI engine with configuration validation.

    Args:
        config_path: Optional path to configuration file

    Returns:
        bool: True if initialization successful, False otherwise
    """
    try:
        config = AIConfig.load_from_file(config_path) if config_path else AIConfig.load_default()

        # Validate configuration
        config.validate()

        # Test AI client connection
        client = get_ai_client(config)
        client.test_connection()

        logger.info("AI engine initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize AI engine: {e}")
        return False


def is_ai_available() -> bool:
    """
    Check if AI capabilities are available.

    Returns:
        bool: True if AI is available and configured, False otherwise
    """
    try:
        config = AIConfig.load_default()
        return config.is_enabled() and config.has_valid_api_key()
    except Exception:
        return False
