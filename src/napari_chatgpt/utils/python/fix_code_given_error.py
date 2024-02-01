import sys
import traceback
from typing import Tuple

import napari
from arbol import asection, aprint
from langchain.callbacks.manager import CallbackManager
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import BaseLLM
from langchain_core.prompts import PromptTemplate

from napari_chatgpt.chat_server.callbacks.callbacks_arbol_stdout import \
    ArbolCallbackHandler
from napari_chatgpt.utils.napari.napari_viewer_info import \
    get_viewer_layers_info
from napari_chatgpt.utils.openai.default_model import \
    get_default_openai_model_name
from napari_chatgpt.utils.python.installed_packages import \
    installed_package_list
from napari_chatgpt.utils.python.python_lang_utils import \
    extract_fully_qualified_function_names, get_function_signature
from napari_chatgpt.utils.strings.extract_code import extract_code_from_markdown


def fix_code_given_error_message(code: str,
                                 error: str,
                                 instructions: str = '',
                                 viewer: 'napari.Viewer' = None,
                                 llm: BaseLLM = None,
                                 verbose: bool = False) -> Tuple[str, bool]:

    with(asection(f'Automatically fix code based on a given error message, code length: {len(code)}')):

        # Cleanup code and error:
        code = code.strip()
        error = error.strip()

        # If code is empty, nothing needs to be fixed!
        if len(code) == 0:
            return code, False

        with asection(f'Code to fix:'):
            aprint(code)
        with asection(f'Error:'):
            aprint(error)

        # By default we don't fix anything:
        fixed_code = str(code)

        try:

            fixed_code = _fix_code_given_error_message(code=code,
                                                       error=error,
                                                       instructions=instructions,
                                                       viewer=viewer,
                                                       llm=llm,
                                                       verbose=verbose)

            return fixed_code

        except Exception as e:
            traceback.print_exc()
            aprint(f"Encoutered exception: {str(e)} while trying to fix code! Returning code unchanged!")
            return fixed_code


_fix_bad_fun_calls_prompt = f"""
**Context:**
You are an expert Python coder with extensive knowledge of all python libraries, and their different versions.
When running the code below:

```python
{'{code}'}
```

I get this error:

```
{'{error}'}
```

**Notes:**
- napari's 'Image' object has no attribute 'multichannel'

The current environment is based on Python version {sys.version.split()[0]} and has the following packages/libraries installed:
{'{package_list}'}. 

{'{layers_info}'}

Below are the function signatures of all function calls detected in the code above:

```
{'{signatures}'}
``` 

{'{instructions}'}

**Task:**
Use these signatures to help you fix the code given the provided error and ensure the fixed code you return is correct and only uses existing classes, methods, fields, functions, and parameters.
Please make only minimal alterations to the code: only change what is absolutely required to fix the code given the provided error.
Do not modify any part of the code that is unrelated to the error. By changing only what is nescessary and sufficient you reduce the chance to introduce new errors.  
Make sure that the code is correct!

**Fixed code:**
"""

def _fix_code_given_error_message(code: str,
                                  error: str,
                                  instructions: str = None,
                                  viewer: 'napari.Viewer' = None,
                                  llm: BaseLLM = None,
                                  verbose: bool = False):

    # Instantiates LLM if needed:
    llm = llm or ChatOpenAI(model_name=get_default_openai_model_name(), temperature=0)

    # Make prompt template:
    prompt_template = PromptTemplate(template=_fix_bad_fun_calls_prompt,
                                     input_variables=['code',
                                                      'error',
                                                      'signatures',
                                                      'package_list',
                                                      'layers_info',
                                                      'instructions'])

    # Instantiate chain:
    chain = LLMChain(
        prompt=prompt_template,
        llm=llm,
        verbose=verbose,
        callback_manager=CallbackManager(
            [ArbolCallbackHandler('fix_code_given_error_message')])
    )

    # List all function calls in code:
    function_calls = extract_fully_qualified_function_names(extract_code_from_markdown(code))

    # get signatures of each function:
    signatures = [get_function_signature(function_call) for function_call,_ in function_calls]

    # turn it into a string:
    signatures_str = '\n\n'.join(signatures)

    # Layer info:
    if viewer:
        layers_info = get_viewer_layers_info(viewer)
        layers_info = 'Below are the layers currently present in the napari viewer:\n'+\
                       layers_info+\
                      'Use this information to help you fix the code given the provided error.\n'
    else:
        layers_info = ''


    # List of installed packages with their versions:
    package_list = installed_package_list()

    # turn it into a string:
    package_list_str = '\n'.join(package_list)

    # Variable for prompt:
    variables = {'code': code,
                 'error': error,
                 'signatures':signatures_str,
                 'package_list': package_list_str,
                 'layers_info': layers_info,
                 'instructions': instructions}

    # call LLM:
    fixed_code = chain(variables)['text']

    # Cleanup:
    fixed_code = fixed_code.strip()

    # Extract code from markdown:
    fixed_code = extract_code_from_markdown(fixed_code)

    return fixed_code
