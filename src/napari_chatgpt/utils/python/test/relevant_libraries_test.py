"""Tests for relevant_libraries.py pure functions."""

from napari_chatgpt.utils.python.relevant_libraries import (
    get_all_essential_packages,
    get_all_relevant_packages,
    get_all_signal_processing_related_packages,
)


def test_essential_packages_returns_list():
    result = get_all_essential_packages()
    assert isinstance(result, list)
    assert len(result) > 0


def test_essential_packages_no_duplicates():
    result = get_all_essential_packages()
    assert len(result) == len(set(result))


def test_essential_packages_contains_key_packages():
    result = get_all_essential_packages()
    assert "numpy" in result
    assert "scipy" in result
    assert "pandas" in result


def test_signal_processing_packages_returns_list():
    result = get_all_signal_processing_related_packages()
    assert isinstance(result, list)
    assert len(result) > 0


def test_signal_processing_packages_no_duplicates():
    result = get_all_signal_processing_related_packages()
    assert len(result) == len(set(result))


def test_relevant_packages_is_superset():
    essential = set(get_all_essential_packages())
    signal = set(get_all_signal_processing_related_packages())
    relevant = set(get_all_relevant_packages())
    assert essential.issubset(relevant)
    assert signal.issubset(relevant)
