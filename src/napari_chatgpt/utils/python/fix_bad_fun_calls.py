import re
import sys
import traceback
from difflib import Differ
from typing import Tuple, Optional

from arbol import asection, aprint

from napari_chatgpt.llm.litemind_api import get_llm
from napari_chatgpt.llm.llm import LLM
from napari_chatgpt.utils.python.installed_packages import installed_package_list
from napari_chatgpt.utils.python.python_lang_utils import (
    extract_fully_qualified_function_names,
    function_exists,
)


def fix_all_bad_function_calls(
    code: str, llm: Optional[LLM] = None, verbose: bool = False
) -> Tuple[str, bool, str]:
    """
    Analyzes Python code to detect and automatically fix calls to non-existent functions using a language model.
    
    This function scans the provided code for function calls that do not correspond to any function in the installed packages. For each such call, it uses an LLM to propose a corrected function call and updates the code accordingly, including adding necessary import statements. If no invalid calls are found, the code is returned unchanged.
    
    Parameters:
        code (str): The Python code to analyze and fix.
        verbose (bool): If True, prints detailed information about the fixing process.
    
    Returns:
        Tuple[str, bool, str]: A tuple containing the potentially fixed code, a boolean indicating whether any changes were made, and a report describing any non-existent function calls found.
    """

    with asection(
        f"Automatically fix bad function calls for code of length: {len(code)}"
    ):

        # Instantiates LLM if needed:
        llm = llm or get_llm()

        # Cleanup code:
        code = code.strip()

        # If code is empty, nothing needs to be fixed!
        if len(code) == 0:
            return code, False, ""

        with asection(f"Code to fix:"):
            aprint(code)

        # By default we don't fix anything:
        fixed_code = str(code)

        try:

            # Perform analysis of function calls in code to check if the functions actually exist:
            # First extract function calls from code:
            function_calls = extract_fully_qualified_function_names(code)

            # Is there at least one non-existing function used?
            one_non_existing_function_used = any(
                not function_exists(fully_qual_fun_name)
                for fully_qual_fun_name, original_function_call in function_calls
            )

            if one_non_existing_function_used:

                # There is at least one function that does not exist:
                function_calls_report = "**NON-EXISTENT FUNCTION REPORT:**\n"
                function_calls_report += "I reviewed the code and verified if the function calls correspond to existing functions within the installed packages. \n"
                function_calls_report += "I discovered that the following function calls are referring to functions that do not exist:\n"
                for fully_qual_fun_name, original_function_call in function_calls:
                    if not function_exists(fully_qual_fun_name):
                        function_calls_report += f"- Function call: '{original_function_call}(...)' refers to an non-existing function: '{fully_qual_fun_name}'!\n"
                function_calls_report += "It is possible that the code is referring to an incorrect version of the library or package.\n"
                function_calls_report += "I recommend changing the import statement and/or the qualified name of the function to a different version.\n"

                with asection("Non-existent function report:"):
                    aprint(function_calls_report)

                for fully_qual_fun_name, original_function_call in function_calls:
                    if not function_exists(fully_qual_fun_name):
                        # get the fix:
                        fixed_function_call = fix_function_call(
                            original_function_call,
                            fully_qual_fun_name,
                            llm=llm,
                            verbose=verbose,
                        )

                        aprint(
                            f"LLM proposes this '{fixed_function_call}' as fix for '{fully_qual_fun_name}' (original: '{original_function_call}')"
                        )

                        # Apply fix:
                        fixed_code = fixed_code.replace(
                            original_function_call, fixed_function_call
                        )

                        # Prepend import:
                        package_name = fixed_function_call.split(".")[0]
                        import_statement = f"import {package_name}\n"
                        aprint(f"Adding this import statemet: {import_statement}")
                        fixed_code = import_statement + fixed_code

                with asection(f"Fixed code:"):
                    aprint(fixed_code)

                differ = Differ()
                result = list(
                    differ.compare(
                        code.splitlines(keepends=True),
                        fixed_code.splitlines(keepends=True),
                    )
                )
                differences_text = "".join(result)

                with asection(f"Differences between original code and fixed code:"):
                    aprint(differences_text)

                return fixed_code, True, function_calls_report
            else:
                aprint(f"No bad function calls detected, no need to fix anything!")

                return fixed_code, False, ""

        except Exception as e:
            traceback.print_exc()
            aprint(
                f"Encoutered exception: {str(e)} while trying to fix code! Returning code unchanged!"
            )
            # TOODOO: if code does not compile maybe use LLM to fix it?
            return code, False, ""


_fix_bad_fun_calls_prompt = f"""
**Context:**
You are an expert Python coder with extensive knowledge of all python libraries and their different versions.

This function call: '{'{call}'}' refers to a non-existent function '{'{fully_qual_fun_name}'}'.
The current environment is based on Python version {sys.version.split()[0]} and has the following packages/libraries installed:
{'{package_list}'}. It is very likely that the function call exists but for a different version of the library! 

**Task:**
Please propose the most likely fix for the function call. 
For example: if I tell you that this function call: 'transform.line' refers to a non existent function: 'skimage.transform.line',
you should return the fully qualified corrected function call: 'skimage.draw.line' as this is the correct call for recent version of scikit-image. 
In any case you should check the list above of packages and their version to return the correct function call.
Important: just return the function call as a single line with no comments before or after!
please enclose the returned fixed function call using apostrophes: '<fully_qualified_fixed_function_call>'.

**Fixed Call:**
"""


def fix_function_call(
    original_function_call: str,
    fully_qual_fun_name: str,
    llm: Optional[LLM] = None,
    verbose: bool = False,
):
    # List of installed packages with their versions:
    """
    Uses a language model to generate a corrected fully qualified function call for a given invalid or non-existent function call.
    
    Parameters:
        original_function_call (str): The original function call string to be fixed.
        fully_qual_fun_name (str): The fully qualified name of the function as found in the code.
    
    Returns:
        str or None: The corrected fully qualified function call as proposed by the language model, or None if parsing fails.
    """
    package_list = installed_package_list()

    # turn it into a string:
    package_list_str = "\n".join(package_list)

    # Variable for prompt:
    variables = {
        "call": original_function_call,
        "package_list": package_list_str,
        "fully_qual_fun_name": fully_qual_fun_name,
    }

    # Instantiates LLM if needed:
    llm = llm or get_llm()

    # call LLM:
    fixed_function_call = llm.generate(
        prompt=_fix_bad_fun_calls_prompt, variables=variables, temperature=0.0
    )

    # extract text from messages:
    fixed_function_call = "\n".join([m.to_plain_text() for m in fixed_function_call])

    # Cleanup:
    fixed_function_call = fixed_function_call.strip()

    # Parse function call:
    fixed_function_call = _parse_function_call(fixed_function_call)

    return fixed_function_call


def _parse_function_call(string):
    """
    Extracts a fully qualified function call from a string enclosed in apostrophes.
    
    If the input string contains apostrophes, returns the first dot-separated identifier sequence found within them. If no such pattern is found, returns None. If the string does not contain apostrophes, returns the original string unchanged.
    
    Parameters:
        string (str): The input string potentially containing a function call in apostrophes.
    
    Returns:
        Optional[str]: The extracted function call, None if not found, or the original string if no apostrophes are present.
    """
    if "'" in string:
        pattern = r"'([a-zA-Z]+(?:\.[a-zA-Z]+)*)'"
        match = re.search(pattern, string)
        if match:
            return match.group(1)
        return None
    else:
        return string
