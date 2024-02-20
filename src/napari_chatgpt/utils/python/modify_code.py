import sys

from arbol import aprint, asection
from langchain.chains import LLMChain
from langchain.llms import BaseLLM
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from napari_chatgpt.chat_server.callbacks.callbacks_arbol_stdout import \
    ArbolCallbackHandler
from napari_chatgpt.utils.openai.default_model import \
    get_default_openai_model_name
from napari_chatgpt.utils.python.installed_packages import \
    installed_package_list
from napari_chatgpt.utils.strings.extract_code import extract_code_from_markdown

_change_code_prompt = f"""
**Context:**
You are an expert Python coder and software engineer specialised in making changes to code upon request.
You understand complex code and how to make precise and sufficient changes to it. 

**Task:**
You are given a piece of Python code and a request. Your task is to make changes to the code that satisfy the request.
The answer should be the code with the requested changes made. Make sure we have the right answer.

**Instructions:**
- Do not change the ideas, purpose, semantics, implementation details, nor calculations present in the code unless requested or necessary.
- Only make the changes that are requested.
- Do not introduce new functions, methods, classes, types, or variables unless requested or necessary.
- Do not change the existing code structure, indentation, or formatting unless requested or necessary.
- If the code does not define any function, that is OK, just make the requested changes to the code.
- The changes should be made in a way that the code remains functional and correct.
- The code should be improved solely according to the request.
- If there is no code, that's OK, just write code according to the request.
- Before writing code, make sure to understand the request and the code. 
- First explain in comments what you are going to do and then write the code.
- If you find in comments a TODO or a FIXME, make sure to address it, taking into consideration of the request below.
- Keep all imports statements at the top of the file and do not add new ones unless requested or necessary.
- Make sure the code is complete, correct, and runs without errors.

**Instructions for using provided viewer instance:**
- Do NOT create a new instance of a napari viewer. Assume one is provided in the variable 'viewer'.
- Do NOT manually add the widget to the napari window by calling viewer.window.add_dock_widget().
- Do NOT use the viewer to add layers to the napari window within the function. Instead, use a return statement to return the result.

**Context:**
- The code is written against Python version: {sys.version.split()[0]}.
- Here is the list of installed packages: {'{installed_packages}'}.

**Code:**

```python
{'{code}'}
```

**Request:**
{'{request}'}

**Changed Code in Markdown Format:**
"""


def modify_code(code: str,
                request: str,
                llm: BaseLLM = None,
                model_name: str = None,
                verbose: bool = False) -> str:
    with(asection(
            f'Modifying code upon request for code of length: {len(code)}')):

        try:

            # Cleanup code:
            code = code.strip()

            #Cleanup request:
            request = request.strip()

            aprint(f'Input code:\n{code}')

            # Instantiates LLM if needed:
            llm = llm or ChatOpenAI(model_name=model_name or get_default_openai_model_name(),
                                    temperature=0)

            # Make prompt template:
            prompt_template = PromptTemplate(template=_change_code_prompt,
                                             input_variables=['code', 'request', 'installed_packages'])

            # Instantiate chain:
            chain = LLMChain(
                prompt=prompt_template,
                llm=llm,
                verbose=verbose,
                callbacks=[ArbolCallbackHandler('Change Code')]
            )

            # List of installed packages:
            package_list = installed_package_list()

            # Variable for prompt:
            variables = {'code': code,
                         'request': request,
                         'installed_packages':' '.join(package_list)}

            # call LLM:
            response = chain.invoke(variables)['text']

            # Extract code from the response:
            modified_code = extract_code_from_markdown(response)

            # Cleanup:
            modified_code = modified_code.strip()

            return modified_code

        except Exception as e:
            import traceback
            traceback.print_exc()
            aprint(e)
            return code



