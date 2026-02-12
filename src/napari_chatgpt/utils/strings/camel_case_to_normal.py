"""Utilities for converting camelCase strings to space-separated lowercase."""

import re


def camel_case_to_lower_case_with_space(string):
    """Convert a camelCase string to lowercase words separated by spaces.

    Args:
        string: The camelCase string to convert.

    Returns:
        The input string with camelCase boundaries replaced by spaces,
        all in lowercase. For example, "myCamelCaseString" becomes
        "my camel case string".
    """
    result = re.sub(
        r"(?<=[a-z0-9])[A-Z]", lambda match: f" {match.group(0).lower()}", string
    )

    # Ensure everything is lower case, including first letter:
    result = result.lower()

    return result
