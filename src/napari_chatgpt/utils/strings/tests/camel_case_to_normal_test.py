"""Tests for camel_case_to_lower_case_with_space()."""

import pytest

from napari_chatgpt.utils.strings.camel_case_to_normal import (
    camel_case_to_lower_case_with_space,
)


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("CamelCase", "camel case"),
        ("simpleTest", "simple test"),
        ("getHTTPResponse", "get httpresponse"),
        ("", ""),
        ("alreadylowercase", "alreadylowercase"),
        ("ABC", "abc"),
        ("get3DImage", "get3 dimage"),
    ],
)
def test_camel_case_to_normal(input_str, expected):
    assert camel_case_to_lower_case_with_space(input_str) == expected
