"""Utilities for cleaning up Python code by removing invalid lines."""

from arbol import aprint


def remove_invalid_python_lines(code: str):
    """Remove lines that are not individually valid Python statements.

    Each line is compiled independently; lines that raise a SyntaxError
    are removed and logged via aprint.

    Args:
        code: A string containing Python code, potentially with
            non-Python text mixed in.

    Returns:
        The code with invalid lines removed, joined by newlines.
    """

    lines = code.splitlines()
    valid_lines = []
    for line in lines:
        try:
            compile(line, "", "exec")
            valid_lines.append(line)
        except SyntaxError:
            aprint(f"Removed this line because not valid python:\n{line}\n")

    return "\n".join(valid_lines)
