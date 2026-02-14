"""Tests for the delegated_code/utils.py module.

These tests verify that the package check functions correctly detect
whether packages are installed without triggering heavy imports
(e.g. TensorFlow via stardist, PyTorch via cellpose).
"""

import importlib.util

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


def test_check_stardist_matches_find_spec():
    """Test that check_stardist_installed agrees with importlib.util.find_spec."""
    stardist_available = importlib.util.find_spec("stardist") is not None
    assert check_stardist_installed() == stardist_available


def test_check_cellpose_matches_find_spec():
    """Test that check_cellpose_installed agrees with importlib.util.find_spec."""
    cellpose_available = importlib.util.find_spec("cellpose") is not None
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
