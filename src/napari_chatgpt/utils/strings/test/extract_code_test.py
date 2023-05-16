from napari_chatgpt.utils.strings.extract_code import extract_code_from_markdown

markdown = """
```python
# some python code
from napari_chatgpt.utils.extract_code import extract_code_from_markdown

def filter_lines(text:str, filter_out: List[str]=None) -> str:
    lines = text.split('\n')
    filtered_lines = [line for line in lines if
                      not any(substring in line for substring in filter_out)]
    return '\n'.join(filtered_lines)

```
"""


def test_extract_urls():
    code = extract_code_from_markdown(markdown)

    print(code)
