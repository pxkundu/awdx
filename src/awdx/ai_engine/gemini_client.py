"""
AWDX AI Engine - Google Gemini Client

This module provides the core client for interacting with Google Gemini API,
including natural language processing, multimodal capabilities, and error handling.

Key Features:
    - Text generation with context management
    - Multimodal processing (images, documents)
    - Automatic retry with exponential backoff
    - Rate limiting and quota management
    - Security and safety filtering
    - Response caching for performance
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Union

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmBlockThreshold, HarmCategory

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from .config_manager import AIConfig, GeminiConfig
from .exceptions import (
    AuthenticationError,
    GeminiAPIError,
    ModelError,
    NetworkError,
    RateLimitError,
    handle_gemini_api_exception,
)

logger = logging.getLogger(__name__)


class ResponseCache:
    """Simple in-memory cache for API responses."""

    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        Initialize cache.

        Args:
            max_size: Maximum number of cached entries
            ttl: Time-to-live in seconds
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Dict[str, Any]] = {}

    def _generate_key(self, prompt: str, model: str, **kwargs) -> str:
        """Generate cache key from request parameters."""
        cache_data = {"prompt": prompt, "model": model, **kwargs}
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()

    def get(self, prompt: str, model: str, **kwargs) -> Optional[str]:
        """Get cached response if available and not expired."""
        key = self._generate_key(prompt, model, **kwargs)

        if key not in self.cache:
            return None

        entry = self.cache[key]
        if datetime.now() > entry["expires_at"]:
            del self.cache[key]
            return None

        logger.debug(f"Cache hit for key: {key[:8]}...")
        return entry["response"]

    def set(self, prompt: str, model: str, response: str, **kwargs) -> None:
        """Cache response with expiration."""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(
                self.cache.keys(), key=lambda k: self.cache[k]["created_at"]
            )
            del self.cache[oldest_key]

        key = self._generate_key(prompt, model, **kwargs)
        self.cache[key] = {
            "response": response,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=self.ttl),
        }

        logger.debug(f"Cached response for key: {key[:8]}...")

    def clear(self) -> None:
        """Clear all cached entries."""
        self.cache.clear()
        logger.info("Response cache cleared")

    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)


class RateLimiter:
    """Rate limiter for API requests."""

    def __init__(self, requests_per_minute: int = 60, burst_limit: int = 10):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute
            burst_limit: Maximum burst requests
        """
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.requests = []
        self.burst_requests = []

    async def acquire(self) -> None:
        """Acquire rate limit slot, waiting if necessary."""
        now = time.time()

        # Clean old requests (older than 1 minute)
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]

        # Clean old burst requests (older than 1 second)
        self.burst_requests = [
            req_time for req_time in self.burst_requests if now - req_time < 1
        ]

        # Check burst limit
        if len(self.burst_requests) >= self.burst_limit:
            wait_time = 1 - (now - self.burst_requests[0])
            if wait_time > 0:
                logger.debug(f"Burst limit reached, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)

        # Check per-minute limit
        if len(self.requests) >= self.requests_per_minute:
            wait_time = 60 - (now - self.requests[0])
            if wait_time > 0:
                logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)

        # Record request
        now = time.time()
        self.requests.append(now)
        self.burst_requests.append(now)


class GeminiClient:
    """
    Client for interacting with Google Gemini API.

    This client provides high-level methods for text generation, multimodal
    processing, and conversation management with built-in error handling,
    retry logic, and performance optimizations.
    """

    def __init__(self, config: AIConfig):
        """
        Initialize Gemini client.

        Args:
            config: AI engine configuration

        Raises:
            ConfigurationError: If configuration is invalid
            GeminiAPIError: If API client cannot be initialized
        """
        if not GEMINI_AVAILABLE:
            raise GeminiAPIError(
                "Google Generative AI library not available. Install with: pip install google-generativeai"
            )

        self.config = config
        self.gemini_config = config.gemini
        self.rate_limiter = RateLimiter(
            requests_per_minute=config.performance.rate_limit,
            burst_limit=config.performance.burst_limit,
        )

        # Initialize cache if enabled
        self.cache = None
        if config.performance.cache_enabled:
            self.cache = ResponseCache(
                max_size=config.performance.max_cache_size,
                ttl=config.performance.cache_ttl,
            )

        # Configure Gemini API
        if self.gemini_config.api_key:
            genai.configure(api_key=self.gemini_config.api_key)
            self.model = genai.GenerativeModel(self.gemini_config.model)
            logger.info(f"Initialized Gemini model: {self.gemini_config.model}")
        else:
            logger.warning("No Gemini API key configured. AI features will be limited.")
            self.model = None

    def is_available(self) -> bool:
        """Check if Gemini client is available and configured."""
        return (
            GEMINI_AVAILABLE
            and self.gemini_config.api_key is not None
            and self.model is not None
        )

    def test_connection(self) -> bool:
        """
        Test connection to Gemini API.

        Returns:
            bool: True if connection successful, False otherwise

        Raises:
            GeminiAPIError: If connection test fails
        """
        if not self.is_available():
            raise GeminiAPIError("Gemini client not available or configured")

        try:
            response = self.model.generate_content("Test connection")
            return response and response.text is not None
        except Exception as e:
            logger.error(f"Gemini API connection test failed: {e}")
            raise handle_gemini_api_exception(e)

    async def generate_text(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate text using Gemini API.

        Args:
            prompt: User prompt/question
            context: Optional conversation context
            system_prompt: Optional system prompt for instructions
            **kwargs: Additional generation parameters

        Returns:
            str: Generated text response

        Raises:
            GeminiAPIError: If API request fails
        """
        if not self.is_available():
            raise GeminiAPIError("Gemini client not available")

        # Build full prompt
        full_prompt = self._build_prompt(prompt, context, system_prompt)

        # Check cache first
        if self.cache:
            cached_response = self.cache.get(
                full_prompt, self.gemini_config.model, **kwargs
            )
            if cached_response:
                return cached_response

        # Apply rate limiting
        await self.rate_limiter.acquire()

        try:
            response = self.model.generate_content(full_prompt)
            if not response or not response.text:
                raise GeminiAPIError("Empty response from API")

            response_text = response.text.strip()

            # Cache response if caching is enabled
            if self.cache:
                self.cache.set(
                    full_prompt, self.gemini_config.model, response_text, **kwargs
                )

            logger.debug(f"Generated text response ({len(response_text)} chars)")
            return response_text

        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            raise handle_gemini_api_exception(e)

    async def generate_text_stream(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> Generator[str, None, None]:
        """
        Generate text using streaming for long responses.

        Args:
            prompt: User prompt/question
            context: Optional conversation context
            system_prompt: Optional system prompt
            **kwargs: Additional generation parameters

        Yields:
            str: Text chunks as they're generated

        Raises:
            GeminiAPIError: If API request fails
        """
        if not self.is_available():
            raise GeminiAPIError("Gemini client not available")

        # Build full prompt
        full_prompt = self._build_prompt(prompt, context, system_prompt)

        # Apply rate limiting
        await self.rate_limiter.acquire()

        try:
            response = self.model.generate_content(full_prompt, stream=True)

            full_response = ""
            for chunk in response:
                if chunk.text:
                    chunk_text = chunk.text
                    full_response += chunk_text
                    yield chunk_text

            logger.debug(f"Generated streaming response ({len(full_response)} chars)")

        except Exception as e:
            logger.error(f"Streaming text generation failed: {e}")
            raise handle_gemini_api_exception(e)

    async def process_multimodal(
        self,
        prompt: str,
        image_paths: Optional[List[Union[str, Path]]] = None,
        document_paths: Optional[List[Union[str, Path]]] = None,
        **kwargs,
    ) -> str:
        """
        Process multimodal content (text + images/documents).

        Args:
            prompt: Text prompt
            image_paths: Optional list of image file paths
            document_paths: Optional list of document file paths
            **kwargs: Additional generation parameters

        Returns:
            str: Generated response based on multimodal input

        Raises:
            GeminiAPIError: If multimodal processing fails
        """
        if not self.is_available():
            raise GeminiAPIError("Gemini client not available")

        if not self.config.features.multimodal:
            raise GeminiAPIError("Multimodal features are disabled in configuration")

        # Apply rate limiting
        await self.rate_limiter.acquire()

        try:
            content_parts = [prompt]

            # Process images
            if image_paths:
                for image_path in image_paths:
                    image_part = await self._process_image(image_path)
                    content_parts.append(image_part)

            # Process documents (convert to text first)
            if document_paths:
                for doc_path in document_paths:
                    doc_text = await self._process_document(doc_path)
                    content_parts.append(f"Document content:\n{doc_text}")

            # Generate response with retry logic
            response = await self._generate_with_retry(
                content_parts, safety_settings=self._get_safety_settings()
            )

            if not response or not response.text:
                raise GeminiAPIError("Empty response from multimodal API")

            response_text = response.text.strip()
            logger.debug(f"Generated multimodal response ({len(response_text)} chars)")
            return response_text

        except Exception as e:
            logger.error(f"Multimodal processing failed: {e}")
            raise handle_gemini_api_exception(e)

    def _build_prompt(
        self,
        prompt: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Build full prompt with context and system instructions."""
        parts = []

        # Add system prompt
        if system_prompt:
            parts.append(f"System: {system_prompt}")

        # Add context
        if context:
            parts.append(f"Context: {context}")

        # Add user prompt
        parts.append(f"User: {prompt}")

        return "\n\n".join(parts)

    def _get_safety_settings(self) -> Dict[HarmCategory, HarmBlockThreshold]:
        """Get safety settings for content generation."""
        # Map string threshold to enum
        threshold_map = {
            "BLOCK_NONE": HarmBlockThreshold.BLOCK_NONE,
            "BLOCK_LOW_AND_ABOVE": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            "BLOCK_MEDIUM_AND_ABOVE": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            "BLOCK_ONLY_HIGH": HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

        threshold = threshold_map.get(
            self.gemini_config.safety_threshold,
            HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        )

        return {
            HarmCategory.HARM_CATEGORY_HARASSMENT: threshold,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: threshold,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: threshold,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: threshold,
        }

    async def _generate_with_retry(self, content, **kwargs) -> Any:
        """Generate content with automatic retry logic."""
        max_retries = self.gemini_config.max_retries
        retry_delay = self.gemini_config.retry_delay

        for attempt in range(max_retries + 1):
            try:
                return self.model.generate_content(content, **kwargs)

            except Exception as e:
                if attempt == max_retries:
                    raise e

                # Check if error is retryable
                if self._is_retryable_error(e):
                    wait_time = retry_delay * (2**attempt)  # Exponential backoff
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise e

    def _is_retryable_error(self, error: Exception) -> bool:
        """Check if an error is retryable."""
        error_str = str(error).lower()
        retryable_patterns = [
            "rate limit",
            "quota exceeded",
            "timeout",
            "connection",
            "network",
            "503",
            "502",
            "429",
        ]
        return any(pattern in error_str for pattern in retryable_patterns)

    async def _process_image(self, image_path: Union[str, Path]) -> Any:
        """Process image file for multimodal input."""
        try:
            # Read image file
            image_path = Path(image_path)
            if not image_path.exists():
                raise GeminiAPIError(f"Image file not found: {image_path}")

            # Check file type
            allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
            if image_path.suffix.lower() not in allowed_extensions:
                raise GeminiAPIError(f"Unsupported image format: {image_path.suffix}")

            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = f.read()

            # Create image part for Gemini
            import PIL.Image

            image = PIL.Image.open(image_path)

            logger.debug(f"Processed image: {image_path.name} ({image.size})")
            return image

        except Exception as e:
            raise GeminiAPIError(f"Failed to process image {image_path}: {str(e)}")

    async def _process_document(self, doc_path: Union[str, Path]) -> str:
        """Process document file and extract text."""
        try:
            doc_path = Path(doc_path)
            if not doc_path.exists():
                raise GeminiAPIError(f"Document file not found: {doc_path}")

            # Read document based on type
            if doc_path.suffix.lower() == ".txt":
                with open(doc_path, "r", encoding="utf-8") as f:
                    content = f.read()
            elif doc_path.suffix.lower() in [".md", ".markdown"]:
                with open(doc_path, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                # For other formats, we'd need additional libraries
                # For now, just read as text and let the user know
                logger.warning(
                    f"Unsupported document format: {doc_path.suffix}. Reading as plain text."
                )
                with open(doc_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

            logger.debug(f"Processed document: {doc_path.name} ({len(content)} chars)")
            return content[:50000]  # Limit document size to avoid context overflow

        except Exception as e:
            raise GeminiAPIError(f"Failed to process document {doc_path}: {str(e)}")

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        stats = {
            "model": self.gemini_config.model,
            "available": self.is_available(),
            "cache_enabled": self.cache is not None,
            "rate_limit_rpm": self.rate_limiter.requests_per_minute,
            "burst_limit": self.rate_limiter.burst_limit,
        }

        if self.cache:
            stats["cache_size"] = self.cache.size()
            stats["cache_max_size"] = self.cache.max_size

        return stats

    def clear_cache(self) -> None:
        """Clear response cache."""
        if self.cache:
            self.cache.clear()
            logger.info("Response cache cleared")

    def __str__(self) -> str:
        """String representation of client."""
        return f"GeminiClient(model={self.gemini_config.model}, available={self.is_available()})"
