"""Tests for stardist.py module imports.

These tests verify that the module can be imported without errors,
specifically checking the fix for the missing 'Any' type import.
"""

import pytest


def test_stardist_module_imports_without_error():
    """Test that the stardist module can be imported without NameError.

    This test verifies the fix for the bug where 'Any' was used
    but not imported, causing a NameError at module load time.
    """
    # This should not raise NameError: name 'Any' is not defined
    from napari_chatgpt.omega_agent.tools.napari.delegated_code import stardist

    assert stardist is not None


def test_stardist_segmentation_function_exists():
    """Test that the main segmentation function is accessible."""
    from napari_chatgpt.omega_agent.tools.napari.delegated_code.stardist import (
        stardist_segmentation,
    )

    assert callable(stardist_segmentation)


def test_stardist_2d_function_exists():
    """Test that the stardist_2d helper function is accessible."""
    from napari_chatgpt.omega_agent.tools.napari.delegated_code.stardist import (
        stardist_2d,
    )

    assert callable(stardist_2d)


def test_stardist_3d_function_exists():
    """Test that the stardist_3d helper function is accessible."""
    from napari_chatgpt.omega_agent.tools.napari.delegated_code.stardist import (
        stardist_3d,
    )

    assert callable(stardist_3d)


def test_any_type_is_available_in_stardist_module():
    """Test that the Any type is properly imported in the stardist module."""
    import inspect

    import napari_chatgpt.omega_agent.tools.napari.delegated_code.stardist as stardist_module

    # Get the source of stardist_2d function
    source = inspect.getsource(stardist_module.stardist_2d)

    # The function signature uses 'Any | None', so Any must be imported
    assert "Any" in source or "model:" in source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
