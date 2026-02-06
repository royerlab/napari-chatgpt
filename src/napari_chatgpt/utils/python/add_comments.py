import sys

from arbol import aprint, asection

from napari_chatgpt.llm.litemind_api import get_llm
from napari_chatgpt.llm.llm import LLM
from napari_chatgpt.utils.python.installed_packages import installed_package_list
from napari_chatgpt.utils.strings.extract_code import extract_code_from_markdown

_add_comments_prompt = """
**Task:**
Add explanatory comments, docstrings (NumPy/SciPy format), and type hints to the code below.
Do not change the code's functionality, structure, or logic.

**Rules:**
- Only add or amend comments, docstrings, and type hints. Do not introduce new functions, classes, or variables.
- Use the code as ground truth — existing comments may be inaccurate.
- Docstrings should include a summary, parameters, and return type.
- Use correct type hints; use `Any` if uncertain. Add necessary typing imports.

**Environment:**
- Python version: {python_version}
- Installed packages: {installed_packages}

**Code:**

```python
{code}
```

**Commented, documented, and type annotated code in markdown format:**
"""


def add_comments(
    code: str, llm: LLM = None, model_name: str = None, verbose: bool = False
) -> str:
    with asection(
        f"Automatically adds comments, docstrings and types for code of length: {len(code)}"
    ):

        try:

            # Cleanup code:
            code = code.strip()

            # If code is empty, nothing to improve!
            if len(code) == 0:
                return ""

            aprint(f"Input code:\n{code}")

            # Instantiates LLM if needed:
            llm = llm or get_llm()

            # List of installed packages:
            package_list = installed_package_list()

            # Python version:
            python_version = sys.version.split()[0]

            # Variable for prompt:
            variables = {
                "code": code,
                "installed_packages": " ".join(package_list),
                "python_version": python_version,
            }

            # call LLM:
            response = llm.generate(
                prompt=_add_comments_prompt, variables=variables, temperature=0.0
            )

            # Extract the response text:
            response_text = response[-1].to_plain_text()

            # Extract code from the response:
            commented_code = extract_code_from_markdown(response_text)

            # Cleanup:
            commented_code = commented_code.strip()

            return commented_code

        except Exception as e:
            import traceback

            traceback.print_exc()
            aprint(e)
            return code
