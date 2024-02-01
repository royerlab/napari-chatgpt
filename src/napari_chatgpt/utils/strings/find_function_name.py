import re


def find_function_name(code: str):
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
    # Define a regular expression pattern to match the @magicgui decorator followed by a function name
    pattern = r"@magicgui\s*(?:\([^)]*\))?\s*def\s+(\w+)\("

    # Use the re.search function to find the first occurrence of the pattern in the string
    match = re.search(pattern, code)

    # If a match is found, extract the function name from the first group of the match object
    if match:
        function_name = match.group(1)
        return function_name
    else:
        return None