import sys
from typing import Optional

from arbol import aprint, asection

from napari_chatgpt.llm.litemind_api import get_llm
from napari_chatgpt.llm.llm import LLM
from napari_chatgpt.utils.python.installed_packages import installed_package_list
from napari_chatgpt.utils.strings.extract_code import extract_code_from_markdown

_change_code_prompt =\
"""
## Context
You are an expert Python programmer and software engineer with a specialization in modifying and improving code based on specific requests. Your expertise includes understanding complex Python code and making precise adjustments to fulfill given requirements without altering the original intent or functionality.

## Your Task
You are presented with a snippet of Python code and a specific request for changes. Your primary objective is to modify the code so it meets the request's requirements. The modifications should be minimal and focused, ensuring the code remains functional and aligned with the initial purpose.

### Requirements
- **Preserve Original Intent:** Do not alter the core ideas, purpose, semantics, implementation details, or calculations of the code unless explicitly required by the request or absolutely necessary for functionality.
- **Minimal Changes:** Only introduce new functions, methods, classes, types, or variables if the request demands it or they are essential for the solution.
- **Code Structure:** Maintain the existing code structure, indentation, and formatting unless changes are necessary to fulfill the request.
- **Imports:** Keep all import statements at the top. Only add new ones if required by the request or necessary for the solution.
- **Functionality:** Ensure the modified code is complete, correct, and runs without errors. Address any TODOs or FIXMEs within the context of the request.
- **Commentary:** Before implementing changes, briefly explain your approach in comments to clarify the rationale behind your modifications.

### Special Instructions for Napari Viewer
If the task involves a napari viewer:
- Assume a napari viewer instance `viewer` is provided. There's no need to instantiate a new one.
- For code that defines a napari widget using `@magicgui`, integrate the widget into the viewer using `viewer.window.add_dock_widget()`.

### Python Environment
- **Python Version:** The code is intended to run on Python version `{python_version}`.
- **Installed Packages:** A list of installed packages is available for reference: `{installed_packages}`.

## Provided Code
```python
{code}
```

## Modification Request
{request}

## Submission Format
Please submit the modified code in Markdown format, ensuring it adheres to the above guidelines and fulfills the request accurately.

## Changed Code in Markdown Format:

"""


def modify_code(
    code: str,
    request: str,
    llm: Optional[LLM] = None,
    model_name: Optional[str] = None,
    verbose: bool = False,
) -> str:
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
