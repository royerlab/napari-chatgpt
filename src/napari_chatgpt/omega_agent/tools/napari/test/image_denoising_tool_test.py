"""Tests for image_denoising_tool.py fixes.

These tests verify the fix for the incorrect sys.platform.uname() call.
"""

import inspect

import pytest


def test_image_denoising_uses_platform_machine():
    """Test that install_aydin uses platform.machine() not sys.platform.uname().

    This test verifies the fix for the bug where sys.platform.uname() was used,
    but sys.platform is a string and doesn't have a uname() method.
    """
    from napari_chatgpt.omega_agent.tools.napari.image_denoising_tool import (
        install_aydin,
    )

    source = inspect.getsource(install_aydin)

    # Should NOT contain the buggy sys.platform.uname()
    assert (
        "sys.platform.uname()" not in source
    ), "install_aydin should not use sys.platform.uname()"

    # Should contain the correct platform.machine()
    assert "platform.machine()" in source, "install_aydin should use platform.machine()"


def test_image_denoising_tool_module_imports():
    """Test that the image_denoising_tool module can be imported."""
    from napari_chatgpt.omega_agent.tools.napari import image_denoising_tool

    assert image_denoising_tool is not None


def test_install_aydin_function_exists():
    """Test that install_aydin function is accessible."""
    from napari_chatgpt.omega_agent.tools.napari.image_denoising_tool import (
        install_aydin,
    )

    assert callable(install_aydin)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
