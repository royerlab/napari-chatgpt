import re
import sys
import traceback
from difflib import Differ
from typing import Tuple

from arbol import asection, aprint
from langchain import PromptTemplate, LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.chat_models import ChatOpenAI
from langchain.llms import BaseLLM

from napari_chatgpt.chat_server.callbacks.callbacks_stdout import \
    ArbolCallbackHandler
from napari_chatgpt.utils.python.installed_packages import \
    installed_package_list
from napari_chatgpt.utils.python.python_lang_utils import \
    extract_fully_qualified_function_names, function_exists

def fix_all_bad_function_calls(code: str,
                               llm: BaseLLM = None,
                               verbose: bool = False) -> Tuple[str, bool]:
    with(asection(f'Automatically fix bad function calls for code of length: {len(code)}')):

        # Cleanup code:
        code = code.strip()

        # If code is empty, nothing needs to be fixed!
        if len(code) == 0:
            return code, False

        with asection(f'Code to fix:'):
            aprint(code)

        # By default we don't fix anything:
        fixed_code = str(code)

        try:

            # Perform analysis of function calls in code to check if the functions actually exist:
            # First extract function calls from code:
            function_calls = extract_fully_qualified_function_names(code)

            # Is there at least one non-existing function used?
            one_non_existing_function_used = any(
                not function_exists(fully_qual_fun_name) for
                fully_qual_fun_name, original_function_call in function_calls)

            if one_non_existing_function_used:

                # There is at least one function that does not exist:
                function_calls_report = '**NON-EXISTENT FUNCTION REPORT:**\n'
                function_calls_report += 'I reviewed the code and verified if the function calls correspond to existing functions within the installed packages. \n'
                function_calls_report += 'I discovered that the following function calls are referring to functions that do not exist:\n'
                for fully_qual_fun_name, original_function_call in function_calls:
                    if not function_exists(fully_qual_fun_name):
                        function_calls_report += f"- Function call: '{original_function_call}(...)' refers to an non-existing function: '{fully_qual_fun_name}'!\n"
                function_calls_report += 'It is possible that the code is referring to an incorrect version of the library or package.\n'
                function_calls_report += "I recommend changing the import statement and/or the qualified name of the function to a different version.\n"

                with asection('Non-existent function report:'):
                    aprint(function_calls_report)

                for fully_qual_fun_name, original_function_call in function_calls:
                    if not function_exists(fully_qual_fun_name):

                        # get the fix:
                        fixed_function_call = fix_function_call(original_function_call, fully_qual_fun_name)
                        aprint(f"LLM proposes this '{fixed_function_call}' as fix for '{fully_qual_fun_name}' (original: '{original_function_call}')")

                        # Apply fix:
                        fixed_code = fixed_code.replace(original_function_call, fixed_function_call)

                        # Prepend import:
                        package_name = fixed_function_call.split('.')[0]
                        import_statement = f'import {package_name}\n'
                        aprint(
                            f'Adding this import statemet: {import_statement}')
                        fixed_code = import_statement + fixed_code


                with asection(f'Fixed code:'):
                    aprint(fixed_code)

                differ = Differ()
                result = list(differ.compare(code.splitlines(keepends=True),
                                             fixed_code.splitlines(keepends=True)))
                differences_text = ''.join(result)

                with asection(f'Differences between original code and fixed code:'):
                    aprint(differences_text)

                return fixed_code, True
            else:
                aprint(f"No bad function calls detected, no need to fix anything!")

                return fixed_code, False

        except Exception as e:
            traceback.print_exc()
            aprint(f"Encoutered exception: {str(e)} while trying to fix code! Returning code unchanged!")
            # TOODOO: if code does not compile maybe use LLM to fix it?
            return code, False


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

def fix_function_call(original_function_call:str,
                      fully_qual_fun_name: str,
                      llm: BaseLLM = None,
                      verbose: bool = False
                      ):

    # Instantiates LLM if needed:
    llm = llm or ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)

    # Make prompt template:
    prompt_template = PromptTemplate(template=_fix_bad_fun_calls_prompt,
                                     input_variables=["call",
                                                      'package_list',
                                                      'fully_qual_fun_name'])

    # Instantiate chain:
    chain = LLMChain(
        prompt=prompt_template,
        llm=llm,
        verbose=verbose,
        callback_manager=CallbackManager(
            [ArbolCallbackHandler('fix_all_bad_function_calls')])
    )

    # List of installed packages with their versions:
    package_list = installed_package_list()

    # turn it into a string:
    package_list_str = '\n'.join(package_list)

    # Variable for prompt:
    variables = {'call': original_function_call,
                 'package_list': package_list_str,
                 'fully_qual_fun_name': fully_qual_fun_name}

    # call LLM:
    fixed_function_call = chain(variables)['text']

    # Cleanup:
    fixed_function_call = fixed_function_call.strip()

    # Parse function call:
    fixed_function_call = _parse_function_call(fixed_function_call)

    return fixed_function_call


def _parse_function_call(string):
    if "'" in string:
        pattern = r"'([a-zA-Z]+(?:\.[a-zA-Z]+)*)'"
        match = re.search(pattern, string)
        if match:
            return match.group(1)
        return None
    else:
        return string