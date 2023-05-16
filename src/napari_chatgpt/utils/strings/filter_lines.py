from typing import List


def filter_lines(text: str, filter_out: List[str] = None) -> str:
    """
    Filters out lines in `text` that contain any of the substrings in `substrings`.

    Args:
        text (str): The input text string.
        filter_out (list): A list of substrings to filter out.

    Returns:
        str: The filtered text string.
    """
    lines = text.split('\n')
    filtered_lines = [line for line in lines if
                      not any(substring in line for substring in filter_out)]
    return '\n'.join(filtered_lines)
