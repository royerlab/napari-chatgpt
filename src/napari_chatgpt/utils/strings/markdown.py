def extract_markdown_blocks(markdown_str, remove_quotes: bool = False):
    """
    Extracts and returns blocks of text and code from a markdown string.

    Args:
    markdown_str (str): A string formatted in markdown.
    remove_quotes (bool, optional): Whether to remove the quotes from the code blocks. Defaults to True.

    Returns:
    List[str]: A list of strings, where each string is a block of text or code.
    """

    blocks = []
    current_block = []
    in_code_block = False

    for line in markdown_str.split('\n'):
        # Check for code block delimiter
        if line.strip().startswith('```'):
            if in_code_block:
                # End of code block
                if not remove_quotes:
                    current_block.append(line)
                blocks.append('\n'.join(current_block))
                current_block = []
                in_code_block = False
            else:
                # Start of code block
                if current_block:
                    # Add the previous text block if exists
                    blocks.append('\n'.join(current_block))
                    current_block = []
                in_code_block = True
                if not remove_quotes:
                    current_block.append(line)

        else:
            current_block.append(line)

    # Add the last block if exists
    if current_block:
        blocks.append('\n'.join(current_block))

    return blocks

