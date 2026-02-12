"""Utilities for extracting parenthesized integers from strings."""


def find_integer_in_parenthesis(string: str) -> tuple[str, int]:
    """Find an integer in parentheses and return it with the cleaned text.

    Locates the first parenthesized integer in the string, extracts it,
    and returns both the integer and the string with the parenthesized
    portion removed.

    Args:
        string: The string to search for a parenthesized integer.

    Returns:
        A tuple of (cleaned_text, integer) where cleaned_text has the
        parenthesized number removed, or None if no parenthesized
        integer is found.
    """

    # Find the index of the first parenthesis.
    start_index = string.find("(")

    # If there is no parenthesis, return None.
    if start_index == -1:
        return None

    # Find the index of the last parenthesis.
    end_index = string.find(")")

    # If there is no closing parenthesis, return None.
    if end_index == -1:
        return None

    # Get the integer between the parenthesis.
    integer = int(string[start_index + 1 : end_index])

    # Get the text without the number in parenthesis.
    text = string[:start_index] + string[end_index + 1 :]

    return text, integer
