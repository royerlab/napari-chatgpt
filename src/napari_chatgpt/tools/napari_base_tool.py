"""A tool for running python code in a REPL."""
import sys
from queue import Queue

from langchain import LLMChain, PromptTemplate
from langchain.callbacks import StdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from napari import Viewer
from pydantic import Field

from napari_chatgpt.tools.async_base_tool import AsyncBaseTool
from napari_chatgpt.utils.installed_packages import installed_package_list

_generic_codegen_instructions="""
Generic Instructions for Python Code Generation:
1) The code should be fully functional and not depend on any missing code, data or computation.
2) Use any standard python library available in python {python_version}, 
3) Use any installed library from this list: "{packages}". Write your code against the installed version of these libraries. 
4) Do not forget any import statements! For example, if you use function scipy.signal.convolve2d() add the statement: import scipy
5) The response should be just pure python code with minimal comments,
and no explanations before or after the python code. 

"""

class NapariBaseTool(AsyncBaseTool):
    """A base tool for that delegates to execution to a sub-LLM and communicates with napari via queues."""

    name: str = "<NAME>"
    description: str = (
        "Enter"
        "Description"
        "Here"
    )
    code_prefix = ''
    prompt: str = None
    to_napari_queue: Queue = Field(default=None)
    from_napari_queue: Queue = Field(default=None)
    llm: ChatOpenAI = Field(default=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0))

    def _run(self, query: str) -> str:
        """Use the tool."""
        try:

            # Instantiate chain:
            chain = LLMChain(
                prompt=self.get_prompt_template(),
                llm=self.llm,
                verbose=True
            )

            # chain.callback_manager.add_handler(ToolCallbackHandler(type(self).__name__))
            chain.callback_manager.add_handler(StdOutCallbackHandler())


            # List of installed packages:
            package_list = installed_package_list()

            generic_codegen_instructions = _generic_codegen_instructions.format(python_version=str(sys.version.split()[0]),
                                                                                packages=', '.join(package_list))

            # Variable for prompt:
            variables = {"input": query,
                         "generic_codegen_instructions": generic_codegen_instructions
                         }

            # call LLM:
            code = chain(variables)['text']

            # Prepend prefix:
            code = self.code_prefix + code

            # aprint(f"code:\n{code}")

            # Setting up delegated fuction:
            delegated_function = lambda v: self._run_code(query, code, v)

            # Send code to napari:
            self.to_napari_queue.put(delegated_function)

            # Get response:
            response = self.from_napari_queue.get()

            if 'success' in response:
                return f'Tool {type(self).__name__} succeeded to do: {query}'
            else:
                return f'Tool {type(self).__name__} failed to do: {query} because of this error or reason: {response}'

            return response


        except Exception as e:
            traceback.print_exc()
            return str(e)

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:
        raise NotImplementedError("This method must be implemented")

    # async def _arun(self, query: str) -> str:
    #     """Use the tool asynchronously."""
    #     raise NotImplementedError(f"{type(self).__name__} does not support async")

    def get_prompt_template(self):

        prompt_template = PromptTemplate(template=self.prompt,
                                         input_variables=["input",
                                                          "generic_codegen_instructions"])

        return prompt_template

