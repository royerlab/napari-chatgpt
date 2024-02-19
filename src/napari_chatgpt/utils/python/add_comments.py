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

_add_comments_prompt = f"""
**Context:**
You are an expert Python coder specialised in documenting code, writing docstrings, and inferring type hints.
You can understand the purpose of complex code and write detailed explanations for it.

**Task:**
You are given a piece of Python code. Your task is to add explanatory comments, detailed docstrings and correct type hints to the code. 
The answer should be the code with comments, docstrings and type hints added. The functionality of the code should remain the same. Make sure we have the right answer.

**Code Semantics:**
- Do not change the ideas, purpose, semantics, implementation details, nor calculations present in the code. 
- Only add or amend comments, docstrings and type hints.
- Do not introduce new functions, methods, classes, types, or variables.
- Do not change the existing code structure, indentation, or formatting.

**Docstrings:**
- When adding dosctrings to methods and functions please use the NumPy/SciPy docstrings format.
- Docstrings should contain a summary, parameters, and return type.
- Use your extensive and expert knowledge in datascience, image processing and analysis to explain the purpose of functions or in the docstring summary.
- If the code does not define any function, that is OK, just add a general docstring at the top of the code.

**Comments:**
- Add comments to explain the purpose of the code, the purpose of the functions, the purpose of the variables, and the purpose of the different parts of the code.
- About existing comments: do not trust existing comments, use the code as the 'ground truth'. 
- Existing comments and docstrings that explain the code might not actually correspond to the code. 
- Make sure to understand the code so that your comments really explain and correspond to the code.

**Types:**
- Please use the correct type hints for function parameters and return types.
- If you are not sure about the type, please use the 'Any' type.
- Do not define types, only use built-in types or types from the typing module. Do not forget to add import statements for the types you use.

**Context:**
- The code is written against Python version: {sys.version.split()[0]}.
- Here is the list of installed packages: {'{installed_packages}'}.

**Code:**

```python
{'{code}'}
```

**Commented, documented, and type annotated code in markdown format:**
"""


def add_comments(code: str,
                 llm: BaseLLM = None,
                 model_name: str = None,
                 verbose: bool = False) -> str:
    with(asection(
            f'Automatically adds comments, docstrings and types for code of length: {len(code)}')):

        try:

            # Cleanup code:
            code = code.strip()

            # If code is empty, nothing to improve!
            if len(code) == 0:
                return ''

            aprint(f'Input code:\n{code}')

            # Instantiates LLM if needed:
            llm = llm or ChatOpenAI(model_name=model_name or get_default_openai_model_name(),
                                    temperature=0)

            # Make prompt template:
            prompt_template = PromptTemplate(template=_add_comments_prompt,
                                             input_variables=["code", 'installed_packages'])

            # Instantiate chain:
            chain = LLMChain(
                prompt=prompt_template,
                llm=llm,
                verbose=verbose,
                callbacks=[ArbolCallbackHandler('Comment Code')]
            )

            # List of installed packages:
            package_list = installed_package_list()

            # Variable for prompt:
            variables = {"code": code, 'installed_packages': ' '.join(package_list)}

            # call LLM:
            response = chain.invoke(variables)['text']

            # Extract code from the response:
            commented_code = extract_code_from_markdown(response)

            # Cleanup:
            commented_code = commented_code.strip()

            return commented_code

        except Exception as e:
            import traceback
            traceback.print_exc()
            aprint(e)
            return code



