import re


def extract_code_from_markdown(markdown: str):
    """
    Extracts all Python code blocks from a Markdown string.
    
    If the input contains Markdown code blocks marked with ```python, returns the concatenated contents of all such blocks separated by two newlines. If no Python code blocks are found, returns the original input unchanged.
    
    Parameters:
        markdown (str): The Markdown-formatted string to extract code from.
    
    Returns:
        str: The extracted Python code blocks joined by double newlines, or the original string if no code blocks are found.
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
