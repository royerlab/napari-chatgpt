import subprocess
import sys
import traceback
from functools import cache
from subprocess import CalledProcessError
from typing import List

from arbol import aprint, asection
from langchain import LLMChain, PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.chat_models import ChatOpenAI
from langchain.llms import BaseLLM

from napari_chatgpt.chat_server.callbacks.callbacks_stdout import \
    ArbolCallbackHandler
from napari_chatgpt.utils.python.installed_packages import is_package_installed

_required_packages_prompt = f"""
**Context:**
You are an expert Python coder with extensive knowledge of all python libraries, and their different versions.

**Task:**
Find the list of "pip installable" packages (packages that can be installed using the 'pip install' command) required to run the Python code provided below. The code is written against Python version {sys.version.split()[0]}.
Please only include packages that are absolutely necessary for running the code. Do not include any other packages. Exclude any dependencies that are already included in the listed packages.
The answer should be a space-delimited list of packages (<list_of_packages>), without any additional text or explanations before or after.
If no additional packages are required to run this code, just return an empty string.
Make sure we have the right answer.

**Code:**

```python
{'{code}'}
```python


**Answer:**
"""


def required_packages(code: str,
                      llm: BaseLLM = None,
                      verbose: bool = False):
    with(asection(
            f'Automatically determines missing packages for code of length: {len(code)}')):
        # Cleanup code:
        code = code.strip()

        # If code is empty, nothing is missing!
        if len(code) == 0:
            return []

        aprint(f'Input code:\n{code}')

        # Instantiates LLM if needed:
        llm = llm or ChatOpenAI(model_name='gpt-3.5-turbo',
                                temperature=0)

        # Make prompt template:
        prompt_template = PromptTemplate(template=_required_packages_prompt,
                                         input_variables=["code"])

        # Instantiate chain:
        chain = LLMChain(
            prompt=prompt_template,
            llm=llm,
            verbose=verbose,
            callback_manager=CallbackManager(
                [ArbolCallbackHandler('Required libraries')])
        )

        # Variable for prompt:
        variables = {"code": code}

        # call LLM:
        list_of_packages_str = chain(variables)['text']

        # Cleanup:
        list_of_packages_str = list_of_packages_str.strip()

        if len(list_of_packages_str)>0:

            # Parse the list:
            list_of_packages = list_of_packages_str.split()

            aprint(f'List of required packages:\n{list_of_packages}')

        else:
            aprint(f'No packages to run this code!')
            return []

    return list_of_packages


def pip_install(packages: List[str],
                ignore_obvious: bool = True,
                special_rules: bool = True) -> bool:
    if ignore_obvious:
        obvious_packages = ['numpy', 'napari', 'magicgui', 'scikit-image', 'scipy']
        aprint(
            f"Removing 'obvious' packages that should be already installed with Omega: {', '.join(obvious_packages)}")
        packages = [p for p in packages if
                    not p in obvious_packages]
        aprint(f'Packages left: {packages}')

    # Ensure it is a list:
    packages = list(packages)

    if special_rules:
        all_packages_str = ', '.join(packages)
        if 'opencv' in all_packages_str:
            packages.append('opencv-contrib-python')

    # TODO: special rules for CUPY and dependencies: https://docs.cupy.dev/en/stable/install.html
    # TODO: use conda to install some packages.

    try:
        with asection(f"Installing up to {len(packages)} packages with pip:"):
            for package in packages:
                pip_install_single_package(package)
        return True
    except CalledProcessError:
        traceback.print_exc()
        return False


@cache
def pip_install_single_package(package: str,
                               upgrade: bool = False,
                               ignore_if_installed: bool = True):

    # Upgrade is a special case:
    if upgrade:
        ignore_if_installed = False

    with asection(f"Pip installing package: {package}"):

        if ignore_if_installed and is_package_installed(package):
            aprint(f'Package {package} is already installed!')
        else:
            command = [sys.executable, "-m", "pip", "install", package]
            if upgrade:
                aprint(f"Upgrade requested!")
                command.append("--upgrade")

            subprocess.check_call(command)

            aprint(f"Installed!")
