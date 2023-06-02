from typing import Tuple


def find_integer_in_parenthesis(string: str) -> Tuple[str, int]:
    """Finds an integer surrounded by parenthesis in a string and returns that integer and the text without the number in parenthesis.

    Args:
      string: The string to search.

    Returns:
      A tuple containing the integer and the text without the number in parenthesis.
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
    integer = int(string[start_index + 1:end_index])

    # Get the text without the number in parenthesis.
    text = string[:start_index] + string[end_index + 1:]

    return text, integer
