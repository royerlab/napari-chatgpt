"""Tests for file_open_tool.py fixes.

These tests verify the fix for the double-negative error message.
"""

import inspect

import pytest


def test_file_open_tool_error_message_no_double_negative():
    """Test that the failure message doesn't have a double negative.

    This test verifies the fix for the bug where the message said
    "none of the image files could not be opened" (double negative)
    instead of "none of the image files could be opened".
    """
    from napari_chatgpt.omega_agent.tools.napari.file_open_tool import (
        NapariFileOpenTool,
    )

    source = inspect.getsource(NapariFileOpenTool)

    # Should NOT contain the double negative
    assert (
        "could not be opened" not in source
    ), "Error message should not have double negative 'could not be opened'"

    # Should contain the correct message
    assert "could be opened" in source, "Error message should say 'could be opened'"


def test_file_open_tool_module_imports():
    """Test that the file_open_tool module can be imported."""
    from napari_chatgpt.omega_agent.tools.napari import file_open_tool

    assert file_open_tool is not None


def test_napari_file_open_tool_class_exists():
    """Test that NapariFileOpenTool class is accessible."""
    from napari_chatgpt.omega_agent.tools.napari.file_open_tool import (
        NapariFileOpenTool,
    )

    assert NapariFileOpenTool is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
