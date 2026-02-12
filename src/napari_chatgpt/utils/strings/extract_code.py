"""Utilities for extracting Python code blocks from Markdown text."""

import re


def extract_code_from_markdown(markdown: str):
    """Extract Python code from Markdown fenced code blocks.

    Finds all ```python ... ``` blocks in the input and joins them
    together. If no Python code blocks are found, returns the input
    string unchanged.

    Args:
        markdown: A string potentially containing Markdown-formatted
            Python code blocks.

    Returns:
        The extracted Python code as a single string, or the original
        input if no Python code blocks are detected.
    """
    if "```python" in markdown and "```" in markdown:

        # Regex:
        regex_str = "`{3}python[\r\n]+(.*?)[\r\n]+`{3}"

        # Find blocks:
        code_blocks = re.findall(regex_str, markdown, re.DOTALL)

        # Join blocks:
        code = "\n\n".join(code_blocks)

        return code
    else:
        # Not Markdown, we return as is:
        return markdown
