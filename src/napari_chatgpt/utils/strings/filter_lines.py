from typing import List


def filter_lines(
    text: str, filter_out: List[str] = None, comment_lines: bool = False
) -> str:
    """
    Process a multiline string by removing or commenting out lines containing specified substrings.
    
    Parameters:
        text (str): The input multiline string to process.
        filter_out (List[str], optional): Substrings used to identify lines for filtering or commenting. If None, no lines are filtered.
        comment_lines (bool, optional): If True, lines containing any substring in `filter_out` are prefixed with '# '. If False, such lines are removed. Defaults to False.
    
    Returns:
        str: The processed multiline string with lines filtered or commented as specified.
    """
    lines = text.split("\n")
    if comment_lines:
        filtered_lines = [
            f"# {line}" if any(substring in line for substring in filter_out) else line
            for line in lines
        ]
    else:
        filtered_lines = [
            line
            for line in lines
            if not any(substring in line for substring in filter_out)
        ]
    return "\n".join(filtered_lines)
