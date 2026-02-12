"""LLM-powered code modification based on natural-language requests.

Uses an LLM to apply targeted modifications to Python code while preserving
the original intent, structure, and formatting.
"""

import sys

from arbol import aprint, asection

from napari_chatgpt.llm.litemind_api import get_llm
from napari_chatgpt.llm.llm import LLM
from napari_chatgpt.utils.python.installed_packages import installed_package_list
from napari_chatgpt.utils.strings.extract_code import extract_code_from_markdown

_change_code_prompt = """
## Task
Modify the Python code below to fulfill the request. Make minimal, focused changes.

### Rules
- Preserve the code's original intent, structure, and formatting unless changes are required by the request.
- Only introduce new functions, classes, or variables if the request demands it.
- Keep imports at the top; add new ones only if needed.
- Ensure the modified code is complete, correct, and runs without errors.
- If the task involves a napari viewer, assume `viewer` is already provided.

### Environment
- Python {python_version}
- Installed packages: {installed_packages}

## Code
```python
{code}
```

## Request
{request}

## Modified code in markdown format:

"""


def modify_code(
    code: str,
    request: str,
    llm: LLM | None = None,
    model_name: str | None = None,
    verbose: bool = False,
) -> str:
    """Modify Python code according to a natural-language request using an LLM.

    If the request is empty, the LLM is asked to address TODO and FIXME
    comments in the code. Returns the original code unchanged on error.

    Args:
        code: Python source code to modify.
        request: Natural-language description of the desired changes.
        llm: LLM instance to use. If None, one is created from model_name.
        model_name: Name of the LLM model to instantiate if llm is None.
        verbose: Whether to enable verbose output.

    Returns:
        The modified Python source code.
    """
    with asection(f"Modifying code upon request for code of length: {len(code)}"):

        try:

            # Cleanup code:
            code = code.strip()

            # Cleanup request:
            request = request.strip()

            # If the request is empty we assume we want to address TODO_ and FIXME_ comments:
            request = request or "Address TODO and FIXME comments in the code."

            aprint(f"Input code:\n{code}")

            # Instantiates LLM if needed:
            llm = llm or get_llm(model_name=model_name)

            # List of installed packages:
            package_list = installed_package_list()

            # get python version:
            python_version = sys.version.split()[0]

            # Variable for prompt:
            variables = {
                "code": code,
                "request": request,
                "python_version": python_version,
                "installed_packages": " ".join(package_list),
            }

            # call LLM:
            response = llm.generate(
                prompt=_change_code_prompt, variables=variables, temperature=0.0
            )

            # Extract the response text:
            response_text = response[-1].to_plain_text()

            # Extract code from the response:
            modified_code = extract_code_from_markdown(response_text)

            # Cleanup:
            modified_code = modified_code.strip()

            return modified_code

        except Exception as e:
            import traceback

            traceback.print_exc()
            aprint(e)
            return code
