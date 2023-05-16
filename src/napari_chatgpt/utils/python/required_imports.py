import sys

from langchain import LLMChain, PromptTemplate
from langchain.callbacks import StdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain.chat_models import ChatOpenAI
from langchain.llms import BaseLLM

from napari_chatgpt.utils.strings.extract_code import extract_code_from_markdown

_required_imports_prompt = f"""
Task:
You competently list all and only necessary import statements required to run without error the following python ({sys.version.split()[0]}) code:

CODE:
#______________
{'{input}'}
#______________

Please include all imports already in the code and add any import statements that are missing but are required for the code to run correctly.
Answer should be should be in markdown format with one import statement per line without explanations before or after.
ANSWER:
"""


def required_imports(code: str,
                     only_missing: bool = False,
                     llm: BaseLLM = None):
    # Cleanup code:
    code = code.strip()

    # If code is empty, nothing is missing!
    if len(code) == 0:
        return []

    # Instantiates LLM if needed:
    llm = llm or ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)

    # Make prompt template:
    prompt_template = PromptTemplate(template=_required_imports_prompt,
                                     input_variables=["input"])

    # Instantiate chain:
    chain = LLMChain(
        prompt=prompt_template,
        llm=llm,
        verbose=True,
        callback_manager=CallbackManager([StdOutCallbackHandler()])
    )

    # Variable for prompt:
    variables = {'input': code}

    # call LLM:
    list_of_imports_str = chain(variables)['text']

    # Extract code:
    list_of_imports_str = extract_code_from_markdown(list_of_imports_str)

    # Parse the list:
    list_of_imports = list_of_imports_str.split('\n')

    return list_of_imports
