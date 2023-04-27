"""A tool for running python code in a REPL."""
import sys
from queue import Queue

from arbol import aprint
from langchain import LLMChain, PromptTemplate
from langchain.callbacks import StdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from napari import Viewer
from pydantic import Field

from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool
from napari_chatgpt.utils.extract_code import extract_code_from_markdown
from napari_chatgpt.utils.filter_lines import filter_lines
from napari_chatgpt.utils.installed_packages import installed_package_list
from napari_chatgpt.utils.missing_libraries import required_libraries, \
    pip_install

_generic_codegen_instructions = """
PYTHON CODE INSTRUCTIONS:
- The code should be fully functional and not depend on any missing code, data or computation.
- Use any functions from the standard python {python_version} library, 
- Use any functions from installed libraries from this list: "{packages}" -- write your code against the installed version of these libraries. 
- ONLY USE parameters or arguments of functions that you are certain exist in the corresponding package or library version!
- Do not forget any import statements! For example, if you use function scipy.signal.convolve2d() add the statement: import scipy
- The response should be just pure python code with minimal comments, and no explanations before or after the python code. 
- When making a copy of an array, do not use this form: array_like.copy(), instead use np.copy(array_like).
- DO NOT EVER use the function input() to ask additional information from the user!
"""


class NapariBaseTool(AsyncBaseTool):
    """A base tool for that delegates to execution to a sub-LLM and communicates with napari via queues."""

    name: str = "<NAME>"
    description: str = (
        "Enter"
        "Description"
        "Here"
    )
    code_prefix: str = ''
    generic_codegen_instructions: str = _generic_codegen_instructions
    prompt: str = None
    to_napari_queue: Queue = Field(default=None)
    from_napari_queue: Queue = Field(default=None)
    llm: ChatOpenAI = Field(default=None)
    return_direct = False

    def _run(self, query: str) -> str:
        """Use the tool."""

        if self.prompt:
            # Instantiate chain:
            chain = LLMChain(
                prompt=self.get_prompt_template(),
                llm=self.llm,
                verbose=True,
                callback_manager=self.callback_manager
            )

            # chain.callback_manager.add_handler(ToolCallbackHandler(type(self).__name__))
            chain.callback_manager.add_handler(StdOutCallbackHandler())

            # List of installed packages:
            package_list = installed_package_list()

            generic_codegen_instructions = self.generic_codegen_instructions.format(
                python_version=str(sys.version.split()[0]),
                packages=', '.join(package_list))

            # Variable for prompt:
            variables = {"input": query,
                         "generic_codegen_instructions": generic_codegen_instructions
                         }

            # call LLM:
            code = chain(variables)['text']

            aprint(f"code:\n{code}")
        else:
            # No code generated because no sub-LLM delegation, delegated_function has the buisness logic.
            code = None

        # Setting up delegated fuction:
        delegated_function = lambda v: self._run_code(query, code, v)

        # Send code to napari:
        self.to_napari_queue.put(delegated_function)

        # Get response:
        response = self.from_napari_queue.get()

        # The response should always contained 'Success' if things went well!
        # if 'Success' in response:
        #     return response
        # else:
        #     return f"Failure: tool {type(self).__name__} failed to satisfy request: '{query}' because: '{response}'\n"

        return response

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:
        """
        This is the code that is executed, see implementations for details,
        must return 'Success: ...' if things went well, otherwise it is failure!
        """
        raise NotImplementedError("This method must be implemented")

    # async def _arun(self, query: str) -> str:
    #     """Use the tool asynchronously."""
    #     raise NotImplementedError(f"{type(self).__name__} does not support async")

    def get_prompt_template(self):

        prompt_template = PromptTemplate(template=self.prompt,
                                         input_variables=["input",
                                                          "generic_codegen_instructions"])

        return prompt_template

    def _prepare_code(self, code: str, markdown: bool = True):

        # extract code from markdown:
        if markdown:
            code = extract_code_from_markdown(code)

        # Prepend prefix:
        code = self.code_prefix + code

        # Remove any viewer instantiation code:
        code = filter_lines(code, ['napari.Viewer(', '= Viewer(', 'gui_qt('])

        # Add spaces around code:
        code = '\n\n' + code + '\n\n'

        # Are there missing libraries that need to be installed?
        libraries = required_libraries(code)

        # Install them:
        pip_install(libraries)

        return code
