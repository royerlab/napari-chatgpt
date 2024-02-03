

def remove_trailing_code(code: str):
    lines = code.split('\n')
    last_indented_line = None

    # Function to check if a line is indented, not assuming specific indentation style
    def is_indented(line):
        return line.startswith((' ', '\t'))

    # Iterate in reverse to find the last indented line:
    for i in range(len(lines) - 1, -1, -1):
        if is_indented(lines[i]):  # Assumes standard 4-space indentation
            last_indented_line = i
            break

    # If we found an indented line, keep all lines up to this point
    if last_indented_line is not None:
        lines = lines[:last_indented_line + 1]
    else:
        # If no indented line was found, return the code as-is
        return code

    # Join the lines back into a single string
    modified_code = '\n'.join(lines)
    return modified_code