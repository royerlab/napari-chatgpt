"""Tests for the delegated_code/utils.py module.

These tests verify that the package check functions actually attempt
to import the packages rather than returning True unconditionally.
"""

import pytest

from napari_chatgpt.omega_agent.tools.napari.delegated_code.utils import (
    check_cellpose_installed,
    check_stardist_installed,
    get_description_of_algorithms,
    get_list_of_algorithms,
)


def test_check_stardist_installed_returns_bool():
    """Test that check_stardist_installed returns a boolean."""
    result = check_stardist_installed()
    assert isinstance(result, bool)


def test_check_cellpose_installed_returns_bool():
    """Test that check_cellpose_installed returns a boolean."""
    result = check_cellpose_installed()
    assert isinstance(result, bool)


def test_check_stardist_actually_checks_import():
    """Test that check_stardist_installed actually tries to import stardist.

    This test verifies the fix for the bug where the function had an empty
    try block and always returned True.
    """
    # We can't guarantee stardist is installed, but we can verify
    # that the function's behavior matches the actual import status
    try:
        import stardist  # noqa: F401

        stardist_available = True
    except ImportError:
        stardist_available = False

    assert check_stardist_installed() == stardist_available


def test_check_cellpose_actually_checks_import():
    """Test that check_cellpose_installed actually tries to import cellpose.

    This test verifies the fix for the bug where the function had an empty
    try block and always returned True.
    """
    # We can't guarantee cellpose is installed, but we can verify
    # that the function's behavior matches the actual import status
    try:
        import cellpose  # noqa: F401

        cellpose_available = True
    except ImportError:
        cellpose_available = False

    assert check_cellpose_installed() == cellpose_available


def test_get_list_of_algorithms_always_includes_classic():
    """Test that classic algorithm is always available."""
    algos = get_list_of_algorithms()
    assert "classic" in algos


def test_get_list_of_algorithms_returns_list():
    """Test that get_list_of_algorithms returns a list."""
    algos = get_list_of_algorithms()
    assert isinstance(algos, list)


def test_get_description_of_algorithms_returns_string():
    """Test that get_description_of_algorithms returns a string."""
    description = get_description_of_algorithms()
    assert isinstance(description, str)
    assert len(description) > 0


def test_get_description_mentions_classic():
    """Test that the description mentions the classic algorithm."""
    description = get_description_of_algorithms()
    assert "classic" in description.lower() or "Classic" in description


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
