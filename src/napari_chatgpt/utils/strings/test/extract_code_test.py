"""Tests for extract_code_from_markdown()."""

from napari_chatgpt.utils.strings.extract_code import extract_code_from_markdown

markdown = """
```python
# some python code
from napari_chatgpt.utils.extract_code import extract_code_from_markdown

def filter_lines(text:str, filter_out: List[str]=None) -> str:
    lines = text.split('\\n')
    filtered_lines = [line for line in lines if
                      not any(substring in line for substring in filter_out)]
    return '\\n'.join(filtered_lines)

```
"""


def test_extract_code_from_markdown():
    code = extract_code_from_markdown(markdown)

    assert code is not None
    assert "def filter_lines" in code
    assert "```" not in code


def test_extract_code_non_markdown():
    plain_code = "x = 1\ny = 2\n"
    result = extract_code_from_markdown(plain_code)
    assert result == plain_code


def test_extract_code_empty_string():
    result = extract_code_from_markdown("")
    assert result == ""
