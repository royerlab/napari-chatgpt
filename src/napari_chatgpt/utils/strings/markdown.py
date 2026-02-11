"""Utilities for parsing and extracting blocks from Markdown text."""


def extract_markdown_blocks(markdown_str, remove_quotes: bool = False):
    """Extract text and code blocks from a Markdown string.

    Splits the input into alternating text and code blocks based on
    triple-backtick (```) delimiters.

    Args:
        markdown_str: A string formatted in Markdown.
        remove_quotes: If True, the triple-backtick fence lines are
            excluded from code blocks. Defaults to False.

    Returns:
        A list of strings, where each string is a contiguous block of
        text or code from the input.
    """

    blocks = []
    current_block = []
    in_code_block = False

    for line in markdown_str.split("\n"):
        # Check for code block delimiter
        if line.strip().startswith("```"):
            if in_code_block:
                # End of code block
                if not remove_quotes:
                    current_block.append(line)
                blocks.append("\n".join(current_block))
                current_block = []
                in_code_block = False
            else:
                # Start of code block
                if current_block:
                    # Add the previous text block if exists
                    blocks.append("\n".join(current_block))
                    current_block = []
                in_code_block = True
                if not remove_quotes:
                    current_block.append(line)

        else:
            current_block.append(line)

    # Add the last block if exists
    if current_block:
        blocks.append("\n".join(current_block))

    return blocks
