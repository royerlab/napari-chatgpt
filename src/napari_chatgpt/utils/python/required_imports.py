import sys

from arbol import asection, aprint
from langchain import LLMChain, PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.chat_models import ChatOpenAI
from langchain.llms import BaseLLM

from napari_chatgpt.chat_server.callbacks.callbacks_stdout import \
    ArbolCallbackHandler
from napari_chatgpt.utils.strings.extract_code import extract_code_from_markdown

_required_imports_prompt = f"""
Task:
You competently list all and only necessary import statements required to run without error the following python ({sys.version.split()[0]}) code:

**CODE:**
#______________
{'{input}'}
#______________

Please include all imports already in the code and add any import statements that are missing but are required for the code to run correctly.
Note: No need to add import statements for the napari viewer, and for the variable 'viewer'.
Answer should be in markdown format with one import statement per line without explanations before or after.

**ANSWER in markdown:**
"""


def required_imports(code: str,
                     llm: BaseLLM = None,
                     verbose: bool = False):
    with(asection(
            f'Automatically determines missing imports for code of length: {len(code)}')):
        # Cleanup code:
        code = code.strip()

        # If code is empty, nothing is missing!
        if len(code) == 0:
            return []

        # Instantiates LLM if needed:
        llm = llm or ChatOpenAI(model_name='gpt-3.5-turbo',
                                temperature=0)

        # Make prompt template:
        prompt_template = PromptTemplate(template=_required_imports_prompt,
                                         input_variables=["input"])

        # Instantiate chain:
        chain = LLMChain(
            prompt=prompt_template,
            llm=llm,
            verbose=verbose,
            callback_manager=CallbackManager(
                [ArbolCallbackHandler('Required imports')])
        )

        # Variable for prompt:
        variables = {'input': code}

        # call LLM:
        list_of_imports_str = chain(variables)['text']

        # Extract code:
        list_of_imports_str = extract_code_from_markdown(list_of_imports_str)

        # Parse the list:
        list_of_imports = list_of_imports_str.split('\n')

        aprint(f'List of missing imports:\n{list_of_imports}')

    return list_of_imports
