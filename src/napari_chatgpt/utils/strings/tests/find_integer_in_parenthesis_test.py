"""Tests for find_integer_in_parenthesis()."""

import pytest

from napari_chatgpt.utils.strings.find_integer_in_parenthesis import (
    find_integer_in_parenthesis,
)


def test_find_integer_in_parenthesis():
    string = "some text (3) and more here"
    text, integer = find_integer_in_parenthesis(string)

    assert text == "some text  and more here"
    assert integer == 3


def test_no_parenthesis():
    assert find_integer_in_parenthesis("no parens") is None


def test_empty_parenthesis():
    # Empty parenthesis causes ValueError in int() - document this behavior
    with pytest.raises(ValueError):
        find_integer_in_parenthesis("text ()")


def test_non_numeric_parenthesis():
    # Non-numeric content causes ValueError in int() - document this behavior
    with pytest.raises(ValueError):
        find_integer_in_parenthesis("text (abc)")


def test_negative_integer():
    text, integer = find_integer_in_parenthesis("text (-5)")
    assert text == "text "
    assert integer == -5


def test_first_match_only():
    text, integer = find_integer_in_parenthesis("text (1) more (2)")
    assert integer == 1
    assert "(2)" in text
