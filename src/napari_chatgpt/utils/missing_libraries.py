import subprocess
import sys
import traceback
from functools import cache
from subprocess import CalledProcessError
from typing import List

from arbol import aprint, asection
from langchain import LLMChain, PromptTemplate
from langchain.callbacks import StdOutCallbackHandler, CallbackManager
from langchain.chat_models import ChatOpenAI
from langchain.llms import BaseLLM

from napari_chatgpt.utils.openai_key import set_openai_key

_pip_install_missing_prompt = f"""
Task:
You competently write the 'pip install <list_of_packages>' command required to run the following python {sys.version.split()[0]} code:

CODE:
#______________
{'{input}'}
#______________

Only list packages that are ABSOLUTELY necessary, NO other packages should be included in the list.
Mandatory dependencies of packages listed should not be included.
Answer should be a space-delimited list of packages (<list_of_packages>) without text or explanations before or after.
ANSWER:
"""


def required_libraries(code: str, llm: BaseLLM = None):
    # Cleanup code:
    code = code.strip()

    # If code is empty, nothing is missing!
    if len(code) == 0:
        return []

    # Ensure that OpenAI key is set:
    set_openai_key()

    # Instantiates LLM if needed:
    llm = llm or ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)

    # Make prompt template:
    prompt_template = PromptTemplate(template=_pip_install_missing_prompt,
                                     input_variables=["input"])

    # Instantiate chain:
    chain = LLMChain(
        prompt=prompt_template,
        llm=llm,
        verbose=True,
        callback_manager=CallbackManager([StdOutCallbackHandler()])
    )

    # Variable for prompt:
    variables = {"input": code}

    # call LLM:
    list_of_packages_str = chain(variables)['text']

    # Parse the list:
    list_of_packages = list_of_packages_str.split()

    return list_of_packages


def pip_install(packages: List[str], ignore_obvious: bool = True) -> bool:
    if ignore_obvious:
        packages = [p for p in packages if
                    not p in ['numpy', 'napari', 'magicgui', 'scikit-image']]

    try:
        with asection(f"Installing {len(packages)} packages with pip:"):
            for package in packages:
                _pip_install_single_package(package)
        return True
    except CalledProcessError:
        aprint(traceback.format_exc())
        return False


@cache
def _pip_install_single_package(package):
    aprint(f"Pip installing package: {package}")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    aprint(f"Installed!")
