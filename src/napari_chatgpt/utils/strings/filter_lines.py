from typing import List


def filter_lines(text: str,
                 filter_out: List[str] = None,
                 comment_lines: bool = False) -> str:
    """
    Filters out lines in `text` that contain any of the substrings in `substrings`.

    Args:
        text (str): The input text string.
        filter_out (list): A list of substrings to filter out.

    Returns:
        str: The filtered text string.
    """
    lines = text.split('\n')
    if comment_lines:
        filtered_lines = [f'# {line}' if any(substring in line for substring in filter_out) else line for line in lines]
    else:
        filtered_lines = [line for line in lines if
                          not any(substring in line for substring in filter_out)]
    return '\n'.join(filtered_lines)
