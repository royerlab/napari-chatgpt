from typing import Tuple


def find_integer_in_parenthesis(string: str) -> Tuple[str, int]:
    """
    Extracts the first integer found within parentheses in a string and returns a tuple of the string with the parentheses and integer removed, and the extracted integer.
    
    Parameters:
        string (str): The input string to search for an integer within parentheses.
    
    Returns:
        tuple[str, int] or None: A tuple containing the modified string (with the parenthesized integer removed) and the extracted integer, or None if parentheses are not found.
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
