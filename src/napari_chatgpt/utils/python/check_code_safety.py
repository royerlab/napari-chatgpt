"""LLM-powered code safety assessment.

Uses an LLM to evaluate Python code and assign a safety rating (A through E)
based on potential risks such as file I/O, network access, and resource usage.
"""

import re
import sys

from arbol import aprint, asection

from napari_chatgpt.llm.litemind_api import get_llm
from napari_chatgpt.llm.llm import LLM
from napari_chatgpt.utils.python.installed_packages import installed_package_list

_check_code_safety_prompt = """
**Task:**
Assess the safety of the Python code below from the user's standpoint and assign a rank:

- **A** — Pure computation, no I/O (no file access, no networking), low resource usage.
- **B** — No I/O, but may use significant memory or CPU (e.g., large array operations, ML inference).
- **C** — Reads existing files or creates new files in expected locations, but no network access and no modification/deletion of existing files.
- **D** — Reads, writes, or modifies files in ways that could be benign or harmful, or accesses the network for plausible purposes (e.g., downloading a dataset).
- **E** — Deletes or overwrites existing files, accesses the network suspiciously, or contains deceptive/malicious code.

**Environment:**
- Python version: {python_version}
- Installed packages: {installed_packages}

**Code:**

```python
{code}
```

**Response Format:**
Explain your ranking with supporting code snippets.
End your response with exactly: 'Rating: *X*' where X is A-E.

**Explanation and rating:**
"""


def check_code_safety(
    code: str, llm: LLM = None, model_name: str = None, verbose: bool = False
) -> str:
    """Assess the safety of Python code using an LLM.

    The LLM evaluates the code and assigns a safety rank from A (pure
    computation, no I/O) to E (destructive or suspicious operations).

    Args:
        code: Python source code to evaluate.
        llm: LLM instance to use. If None, a default is created.
        model_name: Name of the LLM model (unused, reserved for future use).
        verbose: Whether to enable verbose output.

    Returns:
        A tuple of (explanation, rank) where explanation is the LLM's
        reasoning and rank is a single letter A-E, or "Unknown" on failure.
    """
    with asection(f"Checking safety of code of length: {len(code)}"):

        try:

            # Cleanup code:
            code = code.strip()

            # If code is empty, nothing to improve!
            if len(code) == 0:
                return "No code is safe code,", "A"

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
                "python_version": python_version,
                "installed_packages": " ".join(package_list),
            }

            # call LLM:
            response = llm.generate(
                prompt=_check_code_safety_prompt, variables=variables, temperature=0.0
            )

            # Extract the response text:
            response = response[-1].to_plain_text()

            # Cleanup:
            response = response.strip()

            # Find the safety rank in the response using various patterns
            # The LLM may format the rank as *A*, **A**, \*A\*, rated A, Rank: A, etc.
            safety_rank = _extract_safety_rank(response)

            return response, safety_rank

        except Exception as e:
            import traceback

            traceback.print_exc()
            aprint(e)
            return "", "Unknown"


def _extract_safety_rank(response: str) -> str:
    """Extract safety rank (A-E) from LLM response using multiple regex patterns.

    Args:
        response: The full text response from the LLM.

    Returns:
        A single uppercase letter A-E, or "Unknown" if no rank is found.
    """
    # Patterns to match various LLM formatting styles:
    # *A*, **A**, \*A\*, rated A, Rank: A, rating: A, etc.
    patterns = [
        r"\*+\\?\*?([A-E])\\?\*?\*+",  # *A*, **A**, \*A\*, etc.
        r"rated\s+\*?([A-E])\*?",  # rated A, rated *A*
        r"rank[:\s]+\*?([A-E])\*?",  # Rank: A, rank A
        r"rating[:\s]+\*?([A-E])\*?",  # rating: A
        r"is\s+\*?([A-E])\*?[:\s]",  # is A:, is *A*:
        r"\*\*([A-E])\*\*",  # **A** (bold markdown)
    ]

    for pattern in patterns:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            return match.group(1).upper()

    return "Unknown"
