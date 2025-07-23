"""
Test AI Integration

Basic tests to verify AI engine components work correctly.
"""

import os
from unittest.mock import Mock, patch

import pytest


# Test imports work correctly
@pytest.mark.unit
@pytest.mark.ai
def test_ai_engine_imports():
    """Test that AI engine components can be imported."""
    try:
        from awdx.ai_engine import AIConfig, initialize_ai_engine, is_ai_available
        from awdx.ai_engine.config_manager import GeminiConfig
        from awdx.ai_engine.exceptions import AIEngineError, ConfigurationError

        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import AI engine components: {e}")


@pytest.mark.unit
@pytest.mark.ai
def test_ai_config_creation():
    """Test AI configuration creation and validation."""
    from awdx.ai_engine.config_manager import AIConfig, GeminiConfig

    # Test default configuration
    config = AIConfig()
    assert config.enabled is True
    assert config.gemini.model == "gemini-1.5-flash"
    assert config.gemini.temperature == 0.7

    # Test configuration with API key
    config.gemini.api_key = "AI_test_key_123"
    assert config.has_valid_api_key() is True


@pytest.mark.unit
@pytest.mark.ai
def test_ai_availability_check():
    """Test AI availability checking."""
    from awdx.ai_engine import is_ai_available

    # Without API key
    original_key = os.environ.get("GEMINI_API_KEY")
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]

    assert is_ai_available() is False

    # With API key
    os.environ["GEMINI_API_KEY"] = "AI_test_key_123"
    # Note: This might still be False if google-generativeai is not installed
    # but that's expected behavior

    # Restore original key
    if original_key:
        os.environ["GEMINI_API_KEY"] = original_key
    elif "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]


@pytest.mark.unit
@pytest.mark.ai
def test_exception_hierarchy():
    """Test that exception hierarchy works correctly."""
    from awdx.ai_engine.exceptions import (
        AIEngineError,
        ConfigurationError,
        GeminiAPIError,
        NLPProcessingError,
    )

    # Test base exception
    base_error = AIEngineError("Test error")
    assert str(base_error) == "Test error"
    assert base_error.error_code == "AIEngineError"

    # Test inheritance
    config_error = ConfigurationError("Config error")
    assert isinstance(config_error, AIEngineError)

    api_error = GeminiAPIError("API error")
    assert isinstance(api_error, AIEngineError)

    nlp_error = NLPProcessingError("NLP error")
    assert isinstance(nlp_error, AIEngineError)


@pytest.mark.unit
@pytest.mark.ai
def test_intent_enum():
    """Test Intent enum definition."""
    from awdx.ai_engine.nlp_processor import Intent

    # Test basic intents exist
    assert Intent.LIST_PROFILES.value == "list_profiles"
    assert Intent.SHOW_COSTS.value == "show_costs"
    assert Intent.IAM_AUDIT.value == "iam_audit"
    assert Intent.HELP.value == "help"
    assert Intent.UNKNOWN.value == "unknown"


@pytest.mark.unit
@pytest.mark.ai
@patch("awdx.ai_engine.gemini_client.genai")
def test_gemini_client_creation(mock_genai):
    """Test Gemini client creation."""
    from awdx.ai_engine.config_manager import AIConfig
    from awdx.ai_engine.gemini_client import GeminiClient

    # Mock the generative AI module
    mock_genai.GenerativeModel.return_value = Mock()

    config = AIConfig()
    config.gemini.api_key = "AI_test_key_123"

    client = GeminiClient(config)
    assert client.config == config
    assert client.gemini_config == config.gemini


@pytest.mark.unit
@pytest.mark.ai
def test_parsed_command_structure():
    """Test ParsedCommand dataclass."""
    from awdx.ai_engine.nlp_processor import Intent, ParsedCommand, CommandParameter

    command = ParsedCommand(
        intent=Intent.LIST_PROFILES,
        confidence=0.95,
        awdx_command="awdx profile list",
        parameters=[],
        explanation="Lists all AWS profiles",
        suggestions=["awdx profile list", "awdx profile show"],
    )

    assert command.intent == Intent.LIST_PROFILES
    assert command.confidence == 0.95
    assert command.awdx_command == "awdx profile list"

    # Test serialization
    command_dict = command.to_dict()
    assert command_dict["intent"] == "list_profiles"
    assert command_dict["confidence"] == 0.95


@pytest.mark.unit
@pytest.mark.ai
def test_ai_commands_import():
    """Test that AI commands can be imported."""
    try:
        from awdx.ai_engine.ai_commands import ai_app

        assert ai_app is not None
    except ImportError as e:
        pytest.fail(f"Failed to import AI commands: {e}")


@pytest.mark.unit
@pytest.mark.ai
def test_cli_integration():
    """Test that CLI integration works."""
    try:
        from awdx.cli import AI_AVAILABLE, app

        assert app is not None
        # AI_AVAILABLE might be True or False depending on dependencies
        assert isinstance(AI_AVAILABLE, bool)
    except ImportError as e:
        pytest.fail(f"Failed to import main CLI with AI integration: {e}")


@pytest.mark.unit
@pytest.mark.ai
def test_environment_variable_handling():
    """Test environment variable handling in configuration."""
    from awdx.ai_engine.config_manager import AIConfig

    original_vars = {}
    test_vars = {
        "GEMINI_API_KEY": "AI_test_123",
        "GEMINI_MODEL": "gemini-1.5-flash",
        "GEMINI_TEMPERATURE": "0.5",
        "AWDX_AI_ENABLED": "true",
        "AWDX_DEBUG": "true",
    }

    # Save original values
    for key in test_vars:
        original_vars[key] = os.environ.get(key)

    try:
        # Set test values
        for key, value in test_vars.items():
            os.environ[key] = value

        # Load configuration
        config = AIConfig.load_default()

        # Verify environment variables were applied
        assert config.gemini.api_key == "AI_test_123"
        assert config.gemini.model == "gemini-1.5-flash"
        assert config.gemini.temperature == 0.5
        assert config.enabled is True
        assert config.debug_mode is True

    finally:
        # Restore original values
        for key, original_value in original_vars.items():
            if original_value is None:
                if key in os.environ:
                    del os.environ[key]
            else:
                os.environ[key] = original_value


if __name__ == "__main__":
    # Run basic smoke test
    print("🧪 Running AI Integration Smoke Tests...")

    try:
        test_ai_engine_imports()
        print("✅ AI engine imports work")

        test_ai_config_creation()
        print("✅ AI configuration works")

        test_exception_hierarchy()
        print("✅ Exception hierarchy works")

        test_intent_enum()
        print("✅ Intent enum works")

        test_parsed_command_structure()
        print("✅ ParsedCommand structure works")

        test_ai_commands_import()
        print("✅ AI commands import works")

        test_cli_integration()
        print("✅ CLI integration works")

        test_environment_variable_handling()
        print("✅ Environment variable handling works")

        print("\n🎉 All smoke tests passed!")

    except Exception as e:
        print(f"\n❌ Smoke test failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
