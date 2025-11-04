def extract_markdown_blocks(markdown_str, remove_quotes: bool = False):
    """
    Splits a markdown-formatted string into separate text and code blocks.
    
    Parameters:
        markdown_str (str): The markdown content to process.
        remove_quotes (bool, optional): If True, excludes the triple backtick delimiters from code blocks. Defaults to False.
    
    Returns:
        List[str]: A list where each element is a contiguous block of text or code extracted from the input markdown.
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
