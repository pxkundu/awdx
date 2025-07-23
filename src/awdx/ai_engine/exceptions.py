"""
AWDX AI Engine Exceptions

This module defines custom exception classes for the AI engine to provide
clear error handling and debugging information.

Exception Hierarchy:
    AIEngineError (base)
    ├── ConfigurationError
    ├── GeminiAPIError
    │   ├── AuthenticationError
    │   ├── RateLimitError
    │   ├── NetworkError
    │   └── ModelError
    ├── NLPProcessingError
    │   ├── IntentRecognitionError
    │   ├── CommandMappingError
    │   └── ResponseParsingError
    └── ContextError
        ├── SessionExpiredError
        └── ContextOverflowError
"""

import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AIEngineError(Exception):
    """
    Base exception class for all AI engine related errors.

    This is the parent class for all AI engine exceptions and provides
    common functionality for error reporting and logging.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        """
        Initialize the AI engine error.

        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            details: Optional dictionary with additional error details
            cause: Optional underlying exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.cause = cause

        # Log the error for debugging
        logger.error(
            f"{self.error_code}: {message}",
            extra={
                "error_details": self.details,
                "underlying_cause": str(cause) if cause else None,
            },
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "cause": str(self.cause) if self.cause else None,
        }


class ConfigurationError(AIEngineError):
    """
    Raised when there's an issue with AI engine configuration.

    This includes missing configuration files, invalid API keys,
    malformed configuration values, etc.
    """

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        """
        Initialize configuration error.

        Args:
            message: Error message
            config_key: Optional configuration key that caused the error
            **kwargs: Additional arguments passed to parent class
        """
        details = kwargs.get("details", {})
        if config_key:
            details["config_key"] = config_key

        # Filter out error_code from kwargs to avoid duplicate argument
        filtered_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["details", "error_code"]
        }

        super().__init__(
            message=f"Configuration error: {message}",
            error_code="CONFIG_ERROR",
            details=details,
            **filtered_kwargs,
        )


class GeminiAPIError(AIEngineError):
    """
    Base class for Google Gemini API related errors.

    This covers all errors related to communicating with the Gemini API,
    including authentication, rate limits, network issues, and model errors.
    """

    def __init__(self, message: str, status_code: Optional[int] = None, **kwargs):
        """
        Initialize Gemini API error.

        Args:
            message: Error message
            status_code: Optional HTTP status code from API response
            **kwargs: Additional arguments passed to parent class
        """
        details = kwargs.get("details", {})
        if status_code:
            details["status_code"] = status_code

        # Filter out error_code from kwargs to avoid duplicate argument
        filtered_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["details", "error_code"]
        }

        super().__init__(
            message=f"Gemini API error: {message}",
            error_code="GEMINI_API_ERROR",
            details=details,
            **filtered_kwargs,
        )


class AuthenticationError(GeminiAPIError):
    """
    Raised when API authentication fails.

    This typically indicates an invalid or expired API key.
    """

    def __init__(self, message: str = "Invalid or expired API key", **kwargs):
        # Filter out error_code from kwargs to avoid duplicate argument
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != "error_code"}

        super().__init__(message=message, error_code="AUTH_ERROR", **filtered_kwargs)


class RateLimitError(GeminiAPIError):
    """
    Raised when API rate limits are exceeded.

    This indicates too many requests have been made to the API
    within the allowed time window.
    """

    def __init__(
        self,
        message: str = "API rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs,
    ):
        """
        Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Optional seconds to wait before retrying
            **kwargs: Additional arguments passed to parent class
        """
        details = kwargs.get("details", {})
        if retry_after:
            details["retry_after_seconds"] = retry_after

        # Filter out error_code from kwargs to avoid duplicate argument
        filtered_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["details", "error_code"]
        }

        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details=details,
            **filtered_kwargs,
        )


class NetworkError(GeminiAPIError):
    """
    Raised when network connectivity issues occur.

    This covers timeouts, connection failures, and other network-related issues.
    """

    def __init__(self, message: str = "Network connectivity issue", **kwargs):
        # Filter out error_code from kwargs to avoid duplicate argument
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != "error_code"}

        super().__init__(message=message, error_code="NETWORK_ERROR", **filtered_kwargs)


class ModelError(GeminiAPIError):
    """
    Raised when there's an issue with the AI model.

    This includes model unavailability, model errors, or unsupported operations.
    """

    def __init__(
        self,
        message: str = "AI model error",
        model_name: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize model error.

        Args:
            message: Error message
            model_name: Optional name of the model that caused the error
            **kwargs: Additional arguments passed to parent class
        """
        details = kwargs.get("details", {})
        if model_name:
            details["model_name"] = model_name

        # Filter out error_code from kwargs to avoid duplicate argument
        filtered_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["details", "error_code"]
        }

        super().__init__(
            message=message,
            error_code="MODEL_ERROR",
            details=details,
            **filtered_kwargs,
        )


class NLPProcessingError(AIEngineError):
    """
    Base class for natural language processing errors.

    This covers errors in intent recognition, command mapping,
    and response parsing.
    """

    def __init__(self, message: str, user_query: Optional[str] = None, **kwargs):
        """
        Initialize NLP processing error.

        Args:
            message: Error message
            user_query: Optional user query that caused the error
            **kwargs: Additional arguments passed to parent class
        """
        details = kwargs.get("details", {})
        if user_query:
            details["user_query"] = user_query

        # Filter out error_code from kwargs to avoid duplicate argument
        filtered_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["details", "error_code"]
        }

        super().__init__(
            message=f"NLP processing error: {message}",
            error_code="NLP_PROCESSING_ERROR",
            details=details,
            **filtered_kwargs,
        )


class IntentRecognitionError(NLPProcessingError):
    """
    Raised when user intent cannot be recognized from input.

    This occurs when the NLP processor cannot determine what
    the user wants to accomplish.
    """

    def __init__(self, message: str = "Could not recognize user intent", **kwargs):
        # Filter out error_code from kwargs to avoid duplicate argument
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != "error_code"}

        super().__init__(
            message=message, error_code="INTENT_RECOGNITION_ERROR", **filtered_kwargs
        )


class CommandMappingError(NLPProcessingError):
    """
    Raised when recognized intent cannot be mapped to AWDX command.

    This occurs when the system recognizes what the user wants but
    cannot find an appropriate AWDX command to fulfill the request.
    """

    def __init__(
        self,
        message: str = "Could not map intent to command",
        intent: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize command mapping error.

        Args:
            message: Error message
            intent: Optional recognized intent that couldn't be mapped
            **kwargs: Additional arguments passed to parent class
        """
        details = kwargs.get("details", {})
        if intent:
            details["recognized_intent"] = intent

        # Filter out error_code from kwargs to avoid duplicate argument
        filtered_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["details", "error_code"]
        }

        super().__init__(
            message=message,
            error_code="COMMAND_MAPPING_ERROR",
            details=details,
            **filtered_kwargs,
        )


class ResponseParsingError(NLPProcessingError):
    """
    Raised when AI response parsing fails.

    This occurs when the AI returns a response that cannot be parsed
    into the expected format.
    """

    def __init__(
        self,
        message: str = "Could not parse AI response",
        response: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize response parsing error.

        Args:
            message: Error message
            response: Optional AI response that couldn't be parsed
            **kwargs: Additional arguments passed to parent class
        """
        details = kwargs.get("details", {})
        if response:
            details["ai_response"] = response[:500]  # Truncate for logging

        # Filter out error_code from kwargs to avoid duplicate argument
        filtered_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["details", "error_code"]
        }

        super().__init__(
            message=message,
            error_code="RESPONSE_PARSING_ERROR",
            details=details,
            **filtered_kwargs,
        )


class ContextError(AIEngineError):
    """
    Base class for conversation context related errors.

    This covers errors in context management, session handling,
    and context overflow situations.
    """

    def __init__(self, message: str, session_id: Optional[str] = None, **kwargs):
        """
        Initialize context error.

        Args:
            message: Error message
            session_id: Optional session ID that caused the error
            **kwargs: Additional arguments passed to parent class
        """
        details = kwargs.get("details", {})
        if session_id:
            details["session_id"] = session_id

        # Filter out error_code from kwargs to avoid duplicate argument
        filtered_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["details", "error_code"]
        }

        super().__init__(
            message=f"Context error: {message}",
            error_code="CONTEXT_ERROR",
            details=details,
            **filtered_kwargs,
        )


class SessionExpiredError(ContextError):
    """
    Raised when a conversation session has expired.

    This occurs when trying to access context from an expired session.
    """

    def __init__(self, message: str = "Conversation session has expired", **kwargs):
        # Filter out error_code from kwargs to avoid duplicate argument
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != "error_code"}

        super().__init__(
            message=message, error_code="SESSION_EXPIRED_ERROR", **filtered_kwargs
        )


class ContextOverflowError(ContextError):
    """
    Raised when conversation context exceeds limits.

    This occurs when the conversation history becomes too large
    for the AI model to process effectively.
    """

    def __init__(
        self,
        message: str = "Conversation context too large",
        context_size: Optional[int] = None,
        max_size: Optional[int] = None,
        **kwargs,
    ):
        """
        Initialize context overflow error.

        Args:
            message: Error message
            context_size: Optional current context size
            max_size: Optional maximum allowed context size
            **kwargs: Additional arguments passed to parent class
        """
        details = kwargs.get("details", {})
        if context_size:
            details["current_context_size"] = context_size
        if max_size:
            details["max_context_size"] = max_size

        # Filter out error_code from kwargs to avoid duplicate argument
        filtered_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["details", "error_code"]
        }

        super().__init__(
            message=message,
            error_code="CONTEXT_OVERFLOW_ERROR",
            details=details,
            **filtered_kwargs,
        )


# Utility functions for exception handling


def handle_gemini_api_exception(exception: Exception) -> GeminiAPIError:
    """
    Convert various API exceptions to appropriate GeminiAPIError subclasses.

    Args:
        exception: The original exception from the Gemini API

    Returns:
        GeminiAPIError: Appropriate subclass based on the exception type
    """
    error_message = str(exception)

    # Check for specific error patterns in the message
    if "authentication" in error_message.lower() or "api key" in error_message.lower():
        return AuthenticationError(error_message, cause=exception)
    elif (
        "rate limit" in error_message.lower()
        or "quota" in error_message.lower()
        or "429" in error_message
    ):

        # Extract retry_after from the error message if available
        retry_after = None
        if "retry_delay" in error_message:
            match = re.search(r"seconds: (\d+)", error_message)
            if match:
                retry_after = int(match.group(1))

        return RateLimitError(
            message=error_message, retry_after=retry_after, cause=exception
        )
    elif "network" in error_message.lower() or "connection" in error_message.lower():
        return NetworkError(error_message, cause=exception)
    elif "model" in error_message.lower():
        return ModelError(error_message, cause=exception)
    else:
        return GeminiAPIError(error_message, cause=exception)


def format_error_for_user(error: AIEngineError) -> str:
    """
    Format an AI engine error for user-friendly display.

    Args:
        error: The AI engine error to format

    Returns:
        str: User-friendly error message
    """
    if isinstance(error, AuthenticationError):
        return (
            "❌ Authentication failed. "
            "Please check your API key configuration.\n"
            "Visit https://aistudio.google.com/apikey to get your API key.\n"
            "Then run: awdx ai configure"
        )
    elif isinstance(error, RateLimitError):
        retry_after = error.details.get("retry_after_seconds", 60)

        if "quota" in error.message.lower():
            return (
                f"⚠️ API quota exceeded. This is common with the free tier.\n\n"
                f"You can:\n"
                f"• Wait {retry_after} seconds and try again\n"
                f"• Use a simpler query to reduce token usage\n"
                f"• Consider upgrading your Gemini API plan\n"
                f"• Visit https://ai.google.dev/gemini-api/docs/rate-limits for details"
            )
        else:
            return (
                f"⏳ Rate limit exceeded. Please wait {retry_after} seconds before trying again.\n"
                "Consider upgrading your Gemini API plan for higher limits."
            )
    elif isinstance(error, NetworkError):
        return "🌐 Network connectivity issue. Please check your internet connection and try again."
    elif isinstance(error, ConfigurationError):
        return (
            f"⚙️ Configuration error: {error.message}\n"
            "Run 'awdx ai configure' to fix configuration issues."
        )
    elif isinstance(error, IntentRecognitionError):
        return (
            "🤔 I couldn't understand what you want to do.\n"
            "Try rephrasing your request or use 'awdx --help' for available commands."
        )
    else:
        return f"❌ {error.message}"
