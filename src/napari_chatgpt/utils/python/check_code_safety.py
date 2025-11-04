import sys

from arbol import aprint, asection

from napari_chatgpt.llm.litemind_api import get_llm
from napari_chatgpt.llm.llm import LLM
from napari_chatgpt.utils.python.installed_packages import installed_package_list

_check_code_safety_prompt = \
"""
**Context:**
You are an expert Python coder with extensive cybersecurity experience and knowledge. 
You can analyse complex python code and assess its safety from an user standpoint.

**Task:**
You are given a piece of Python code. Your task is to first assess what the code does and whether it is a threat to the user's machine and files.
You then rank the piece code as follows: 
- A -> The code is super safe. It does not have any IO of any kind (no accessing or deleting files, no networking, etc... ), and is expected to use very little memory and cpu.
- B -> The code is relatively safe. It does not have any IO of any kind, but it does some complex calculations and might use a lot of memory or cpu.
- C -> The code is somewhat safe. It does read files but does nothing suspicious with them, and creates new files, It does not accesses the network. 
- D -> The code is somewhat unsafe. It reads, writes files or accesses the network in ways that might be OK, or not.
- E -> The code is unsafe. It writes or deletes files that might already exist, or accesses the network in a suspicious manner. 

**Notes:**
- Code that is deceptive or malicious should be rated as unsafe. 

**Context:**
- The code is written against Python version: {python_version}.
- Here is the list of installed packages: {installed_packages}.

**Code:**

```python
{code}
```

**Response Format:**
Please return an explanation for your ranking and snippets of code that support your judgement.
The answer must contain the rank surrounded with asterisks. 
For example you can write: 'For the reasons stated above, the code is rated *B*', or 'The code is rated *B* because...'.

**Explanation of ranking and rank itself:**
"""


def check_code_safety(
    code: str, llm: LLM = None, model_name: str = None, verbose: bool = False
) -> str:
    """
    Analyze a Python code snippet for cybersecurity safety using a large language model.
    
    The function evaluates the provided code string, passing it along with the current Python version and installed packages to an LLM using a predefined prompt. It returns the LLM's explanation and a categorical safety rank ("A" to "E") based on the analysis. If the code is empty, it returns a default safe message and rank "A". In case of errors during processing, it returns an empty string and rank "Unknown".
    
    Parameters:
        code (str): The Python code to be analyzed.
    
    Returns:
        tuple: A tuple containing the LLM's explanation (str) and the extracted safety rank (str).
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

            # Find the upper case letter between asterisks, for example A in *A*, buy serachinhg for the four ranks: *A*, *B*, *C*, *D*, *E*:
            if "*A*" in response or "*Rank: A*" in response:
                safety_rank = "A"
            elif "*B*" in response or "*Rank: B*" in response:
                safety_rank = "B"
            elif "*C*" in response or "*Rank: C*" in response:
                safety_rank = "C"
            elif "*D*" in response or "*Rank: D*" in response:
                safety_rank = "D"
            elif "*E*" in response or "*Rank: E*" in response:
                safety_rank = "E"
            else:
                safety_rank = "Unknown"

            return response, safety_rank

        except Exception as e:
            import traceback

            traceback.print_exc()
            aprint(e)
            return "", "Unknown"
