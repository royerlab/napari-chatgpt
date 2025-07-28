import sys
from typing import Optional, List

from arbol import aprint, asection

from napari_chatgpt.llm.litemind_api import get_llm
from napari_chatgpt.llm.llm import LLM

_required_packages_prompt =\
"""
**Context:**
You are a highly knowledgeable Python expert, familiar with all pip-installable libraries and their dependencies.

**Task:**
Given the Python code below (targeting Python {python_version}), identify the minimal set of packages that must be installed via `pip install` for the code to run.  

**Instructions:**
- Only list packages that are strictly required and not part of the Python standard library.  
- Exclude packages that are dependencies of other listed packages
- When in doubt, err on the side of inclusion.  
- Do not include explanations, version numbers, or extra text.
- Output a single line with the required package names, separated by spaces (e.g., `numpy scipy magicgui`).  
- If no packages are needed, return an empty string.

**Code:**

```python
{code}
```

**Space Separated List of Packages:**
"""


def required_packages(code: str, llm: Optional[LLM] = None) -> List[str]:
    """
    Determine the minimal set of pip-installable packages required to run a given Python code snippet.
    
    Parameters:
        code (str): The Python code snippet to analyze.
    
    Returns:
        List[str]: A list of unique package names required to execute the code. Returns an empty list if no external packages are needed or if the input is empty.
    """

    with asection(
        f"Automatically determines missing packages for code of length: {len(code)}"
    ):
        # Cleanup code:
        code = code.strip()

        # If code is empty, nothing is missing!
        if len(code) == 0:
            return []

        with asection(f"Input code:"):
            aprint(code)

        variables = {"python_version": sys.version.split()[0], "code": code}

        # Instantiates LLM if needed:
        llm = llm or get_llm()

        # Call LLM:
        list_of_packages_str = llm.generate(
            prompt=_required_packages_prompt, variables=variables, temperature=0.0
        )

        # Extract text from messages:
        list_of_packages_str = "\n".join(
            [m.to_plain_text() for m in list_of_packages_str]
        )

        # Cleanup:
        list_of_packages_str = list_of_packages_str.strip()

        # Sometimes some models insist on having some text before:
        if ":" in list_of_packages_str:
            list_of_packages_str = list_of_packages_str.split(":")[-1].strip()

        # If the string contains commas:
        if "," in list_of_packages_str:
            list_of_packages_str = list_of_packages_str.replace(",", " ")

        # If the string contains new lines:
        if "\n" in list_of_packages_str:
            list_of_packages_str = list_of_packages_str.replace("\n", " ")

        if len(list_of_packages_str) > 0:

            # Parse the list:
            list_of_packages = list_of_packages_str.split()

            # Remove duplicates:
            list_of_packages = list(set(list_of_packages))

            # Strip each package name of white spaces:
            list_of_packages = [p.strip() for p in list_of_packages]

            # Remove empty strings:
            list_of_packages = [p for p in list_of_packages if len(p) > 0]

            aprint(f"List of required packages:\n{list_of_packages}")

        else:
            aprint(f"No packages to run this code!")
            return []

    # Normalise the list of packages and remove duplicates:
    list_of_packages = list(set(list_of_packages))

    return list_of_packages
