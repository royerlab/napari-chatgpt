"""Utilities for finding function names in Python source code strings."""

import re


def find_function_name(code: str):
    """Find the name of the first function defined in a code string.

    Args:
        code: A string containing Python source code.

    Returns:
        The name of the first function found, or None if no function
        definition is present.
    """
    # Define a regular expression pattern to match the function name
    pattern = r"def\s+(\w+)\("

    # Use the re.search function to find the first occurrence of the pattern in the string
    match = re.search(pattern, code)

    # If a match is found, extract the function name from the first group of the match object
    if match:
        function_name = match.group(1)
        return function_name
    else:
        return None


def find_magicgui_decorated_function_name(code: str):
    """Find the name of the first function decorated with @magicgui.

    Scans the code line by line looking for a ``@magicgui`` decorator,
    then extracts the name of the immediately following function
    definition.

    Args:
        code: A string containing Python source code.

    Returns:
        The name of the magicgui-decorated function, or None if no
        such function is found.
    """
    # Split the code into lines:
    lines = code.split("\n")

    # Flag to indicate whether @magicgui has been found:
    found_magicgui = False

    for line in lines:
        # Check if the current line contains @magicgui:
        if "@magicgui" in line.strip():
            found_magicgui = True

        # If @magicgui was found, look for the next function definition
        elif found_magicgui and line.strip().startswith("def"):
            # Extract the function name
            start = line.find("def") + 4
            end = line.find("(")

            # Extract the function name from the line:
            function_name = line[start:end].strip()
            return function_name

    return None
