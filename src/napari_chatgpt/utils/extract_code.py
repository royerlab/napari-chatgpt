import re


def extract_code_from_markdown(markdown: str):
    regex_str = "`{3}python[\r\n]+(.*?)[\r\n]+`{3}"
    # r"```python\n(.*?)```"
    code_blocks = re.findall(regex_str, markdown, re.DOTALL)

    code = '\n\n'.join(code_blocks)

    return code
