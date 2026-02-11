"""Utilities for filtering lines from text based on substring matching."""


def filter_lines(
    text: str, filter_out: list[str] | None = None, comment_lines: bool = False
) -> str:
    """Filter out or comment lines containing specified substrings.

    Args:
        text: The input text string.
        filter_out: A list of substrings. Lines containing any of these
            substrings will be filtered or commented out.
        comment_lines: If True, matching lines are prefixed with '# '
            instead of being removed entirely.

    Returns:
        The filtered text string with matching lines removed or
        commented out.
    """
    lines = text.split("\n")
    filter_out = filter_out or []
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
