from arbol import aprint


def remove_invalid_python_lines(code: str):
    """Removes any text line that is not valid Python from a string.

    Args:
      string: The string to be processed.

    Returns:
      The string with any invalid Python lines removed.
    """

    lines = code.splitlines()
    valid_lines = []
    for line in lines:
        try:
            compile(line, "", "exec")
            valid_lines.append(line)
        except SyntaxError:
            aprint(f"Removed this line because not valid python:\n{line}\n")
            pass

    return "\n".join(valid_lines)
