"""Tests for check_api_key.py fixes.

These tests verify the fix for using the modern OpenAI API
instead of the deprecated v0.x API.
"""

import inspect

import pytest


def test_check_api_key_uses_modern_openai_api():
    """Test that check_openai_api_key uses the modern OpenAI API.

    This test verifies the fix for the bug where the deprecated
    openai.error.AuthenticationError was used instead of the
    modern openai.AuthenticationError.
    """
    from napari_chatgpt.utils.openai.check_api_key import check_openai_api_key

    source = inspect.getsource(check_openai_api_key)

    # Should NOT use deprecated openai.error.AuthenticationError
    assert (
        "openai.error.AuthenticationError" not in source
    ), "Should not use deprecated openai.error.AuthenticationError"

    # Should use modern AuthenticationError import
    assert "AuthenticationError" in source, "Should use modern AuthenticationError"


def test_check_api_key_uses_openai_client():
    """Test that check_openai_api_key uses the OpenAI client pattern.

    The modern OpenAI API uses OpenAI(api_key=...) client pattern
    instead of setting openai.api_key directly.
    """
    from napari_chatgpt.utils.openai.check_api_key import check_openai_api_key

    source = inspect.getsource(check_openai_api_key)

    # Should use OpenAI client
    assert "OpenAI(" in source, "Should use OpenAI client pattern"


def test_check_api_key_does_not_use_chatcompletion():
    """Test that check_openai_api_key doesn't use deprecated ChatCompletion.

    The modern OpenAI API uses client.chat.completions.create()
    instead of openai.ChatCompletion.create().
    """
    from napari_chatgpt.utils.openai.check_api_key import check_openai_api_key

    source = inspect.getsource(check_openai_api_key)

    # Should NOT use deprecated ChatCompletion
    assert "ChatCompletion" not in source, "Should not use deprecated ChatCompletion"


def test_check_api_key_function_exists():
    """Test that check_openai_api_key function is accessible."""
    from napari_chatgpt.utils.openai.check_api_key import check_openai_api_key

    assert callable(check_openai_api_key)


def test_check_api_key_returns_bool():
    """Test that check_openai_api_key returns a boolean."""
    from napari_chatgpt.utils.openai.check_api_key import check_openai_api_key

    # Test with an invalid API key
    result = check_openai_api_key("invalid-key")
    assert isinstance(result, bool)


def test_check_api_key_with_invalid_key_returns_false():
    """Test that check_openai_api_key returns False for invalid keys."""
    from napari_chatgpt.utils.openai.check_api_key import check_openai_api_key

    result = check_openai_api_key("sk-invalid-key-12345")
    assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
