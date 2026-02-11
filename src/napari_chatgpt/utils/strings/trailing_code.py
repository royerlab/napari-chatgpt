"""Utilities for removing trailing unindented code from Python source."""


def remove_trailing_code(code: str):
    """Remove trailing unindented lines from a code string.

    Finds the last indented line in the code and discards everything
    after it. This is useful for stripping extraneous text or comments
    that an LLM may append after the actual code body.

    Args:
        code: A string containing Python source code.

    Returns:
        The code truncated after the last indented line, or the
        original code if no indented lines are found.
    """
    lines = code.split("\n")
    last_indented_line = None

    # Function to check if a line is indented, not assuming specific indentation style
    def is_indented(line):
        return line.startswith((" ", "\t"))

    # Iterate in reverse to find the last indented line:
    for i in range(len(lines) - 1, -1, -1):
        if is_indented(lines[i]):  # Assumes standard 4-space indentation
            last_indented_line = i
            break

    # If we found an indented line, keep all lines up to this point
    if last_indented_line is not None:
        lines = lines[: last_indented_line + 1]
    else:
        # If no indented line was found, return the code as-is
        return code

    # Join the lines back into a single string
    modified_code = "\n".join(lines)
    return modified_code
