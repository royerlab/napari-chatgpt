"""A tool for running python code in a REPL."""
import sys
from pathlib import Path
from queue import Queue
from typing import Union, Optional

import napari
import numpy
from arbol import aprint, asection
from langchain import LLMChain, PromptTemplate
from langchain.chat_models.base import BaseChatModel
from langchain.llms.base import LLM
from langchain.schema.language_model import BaseLanguageModel
from napari import Viewer
from pydantic import Field

from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool
from napari_chatgpt.utils.python.exception_guard import ExceptionGuard
from napari_chatgpt.utils.python.fix_bad_fun_calls import \
    fix_all_bad_function_calls
from napari_chatgpt.utils.python.installed_packages import \
    installed_package_list
from napari_chatgpt.omega.tools.instructions import \
    omega_generic_codegen_instructions
from napari_chatgpt.utils.python.missing_packages import required_packages
from napari_chatgpt.utils.python.pip_utils import pip_install
from napari_chatgpt.utils.python.required_imports import required_imports
from napari_chatgpt.utils.strings.extract_code import extract_code_from_markdown
from napari_chatgpt.utils.strings.filter_lines import filter_lines


def _get_delegated_code(name: str, signature: bool = False):
    with asection(f"Getting delegated code: '{name}' (signature={signature})"):
        # Get current package folder:
        current_package_folder = Path(__file__).parent

        # Get package folder:
        package_folder = Path.joinpath(current_package_folder, f"delegated_code")

        # file path:
        file_path = Path.joinpath(package_folder, f"{name}.py")
        aprint(f'Filepath: {file_path}')

        # code:
        code = file_path.read_text()

        # extract signature:
        if signature:
            aprint('Extracting signature!')
            splitted_code = code.split('### SIGNATURE')
            code = splitted_code[1]

        return code

class NapariBaseTool(AsyncBaseTool):
    """A base tool for that delegates to execution to a sub-LLM and communicates with napari via queues."""

    name: str = "<NAME>"
    description: str = (
        "Enter"
        "Description"
        "Here"
    )
    code_prefix: str = ''
    instructions: str = omega_generic_codegen_instructions
    prompt: str = None
    to_napari_queue: Queue = Field(default=None)
    from_napari_queue: Queue = Field(default=None)
    llm: Union[BaseChatModel, LLM, BaseLanguageModel] = Field(default=None)
    return_direct: bool = False
    save_last_generated_code: bool = True

    fix_imports = True
    install_missing_packages = True
    fix_bad_calls = False

    verbose = False

    last_generated_code: Optional[str] = None

    def _run(self, query: str) -> str:
        """Use the tool."""

        if self.prompt:
            # Instantiate chain:
            chain = LLMChain(
                prompt=self._get_prompt_template(),
                llm=self.llm,
                verbose=self.verbose,
                callbacks=self.callbacks
            )

            # chain.callback_manager.add_handler(ToolCallbackHandler(type(self).__name__))
            # chain.callbacks.add_handler(ArbolCallbackHandler())

            # List of installed packages:
            package_list = installed_package_list()

            if self.last_generated_code:
                last_generated_code = "**Previously Generated Code:**\n",
                last_generated_code += ("Use this code for reference, usefull if you need to modify or fix the code. ",
                                        "IMPORTANT: This code might not be relevant to the current request or task! "
                                        "You should ignore it, unless you are  explicitely asked to fix or modify the last generated widget!",
                                         "```python\n",
                                         self.last_generated_code + '\n',
                                         "```\n"
                                        )
            else:
                last_generated_code = ''

            # Adding information about packages and Python version to instructions:
            filled_generic_instructions = omega_generic_codegen_instructions.format(
                python_version=str(sys.version.split()[0]),
                packages=', '.join(package_list))

            # Prepend generic instructions to tool specific instructions:
            instructions = filled_generic_instructions + self.instructions

            # Variable for prompt:
            variables = {"input": query,
                         "instructions": instructions,
                         "last_generated_code": last_generated_code,
                         }

            # call LLM:
            code = chain(variables)['text']

            aprint(f"code:\n{code}")
        else:
            # No code generated because no sub-LLM delegation, delegated_function has the buisness logic.
            code = None

        # Update last generated code:
        if self.save_last_generated_code:
            self.last_generated_code = code

        # Setting up delegated fuction:
        delegated_function = lambda v: self._run_code(query, code, v)

        # Send code to napari:
        self.to_napari_queue.put(delegated_function)

        # Get response:
        response = self.from_napari_queue.get()

        if isinstance(response, ExceptionGuard):
            exception_guard = response
            # raise exception_guard.exception
            return f"Error: {exception_guard.exception_type_name} with message: '{str(exception_guard.exception)}' while using tool: {self.__class__.__name__} ."

        return response

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:
        """
        This is the code that is executed, see implementations for details,
        must return 'Success: ...' if things went well, otherwise it is failure!
        """
        raise NotImplementedError("This method must be implemented")

    def _get_prompt_template(self):

        prompt_template = PromptTemplate(template=self.prompt,
                                         input_variables=["input",
                                                          "last_generated_code",
                                                          "instructions"])

        return prompt_template

    def _prepare_code(self,
                      code: str,
                      markdown: bool = True,
                      do_fix_bad_calls: bool = True):

        with asection(f"NapariBaseTool: _prepare_code(markdown={markdown}) "):

            with asection(f"code to prepare:"):
                aprint(code)

            # extract code from markdown:
            if markdown:
                code = extract_code_from_markdown(code)

            # Prepend prefix:
            code = self.code_prefix + code

            # Add spaces around code:
            code = '\n\n' + code + '\n\n'

            if self.fix_imports:
                # Are there any missing imports?
                imports = required_imports(code, llm=self.llm)

                # prepend missing imports:
                code = '\n'.join(imports) + '\n\n' + code

            # Fix code, this takes care of wrong function calls and more:
            if self.fix_bad_calls and do_fix_bad_calls:
                code, _ = fix_all_bad_function_calls(code)

            # Remove any offending lines:
            code = filter_lines(code,
                                ['napari.Viewer(', '= Viewer(', 'gui_qt(', 'viewer.window.add_dock_widget('])

            with asection(f"code after all preparations and fixes:"):
                aprint(code)

            if self.install_missing_packages:
                # Are there missing libraries that need to be installed?
                packages = required_packages(code, llm=self.llm)

                # Install them:
                pip_install(packages)

            # Return fully prepared and fixed code:
            return code




def _generate_viewer_info(viewer):
    layer_info = '**Napari viewer information:**'
    layer_info += "| Layer Type | Properties |\n| --- | --- |\n"

    for layer in viewer.layers:
        properties = ""

        # Layer type
        properties += f"| {layer.__class__.__name__} | "

        # Image layer
        if isinstance(layer, napari.layers.Image):
            properties += f"dtype: {layer.data.dtype}, "
            properties += f"shape: {layer.data.shape}, "
            properties += f"min: {numpy.min(layer.data)}, "
            properties += f"max: {numpy.max(layer.data)} "

        # Label layer
        elif isinstance(layer, napari.layers.Labels):
            properties += f"Number of labels: {len(layer.data)} "

        # # Other layer types
        # else:
        #     # Add relevant and similarly useful information for other layer types
        #     properties += "Additional information goes here "

        properties += "|\n"
        layer_info += properties

    return layer_info

