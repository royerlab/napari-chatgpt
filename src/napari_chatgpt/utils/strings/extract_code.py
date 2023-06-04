import re


def extract_code_from_markdown(markdown: str):

    if '```python' in markdown and '```' in  markdown:

        # Regex:
        regex_str = "`{3}python[\r\n]+(.*?)[\r\n]+`{3}"

        # Find blocks:
        code_blocks = re.findall(regex_str, markdown, re.DOTALL)

        # Join blocks:
        code = '\n\n'.join(code_blocks)

        return code
    else:
        # Not Markdown, we return as is:
        return markdown
