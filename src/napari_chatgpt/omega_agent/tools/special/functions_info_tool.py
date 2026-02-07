"""A tool for running python code in a REPL."""

import traceback

from arbol import aprint, asection

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool
from napari_chatgpt.utils.llm.summarizer import summarize
from napari_chatgpt.utils.python.python_lang_utils import (
    extract_package_path,
    get_function_info,
)


class PythonFunctionsInfoTool(BaseOmegaTool):
    """
    A tool for querying the signature and docstrings of python functions.
    This tool can be used to get information about any python function or library function.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "PythonFunctionsInfoTool"
        self.description = (
            "Use this tool for querying the signature and docstrings of python and library functions from their fully qualified name. "
            "For example, send: 'scipy.ndimage.convolve' and this tool will returns the full signature of this function "
            "with all its parameters and if possible corresponding type hints. "
            "You can use this tool to check the correct signature of functions before writing python code, or when errors are encountered."
            "If you want the whole docstring to get a better understanding of the function, its parameters, "
            "and example usages, please prefix your request with the single star character '*'."
        )

    def run_omega_tool(self, query: str = ""):

        with asection(f"PythonFunctionsInfoTool:"):
            with asection(f"Query:"):
                aprint(query)

            add_docstrings = False

            if "*" in query:
                query = query.replace("*", "")
                add_docstrings = True
                aprint("Agent asked for docstrings!")

            function_path_and_name = query
            try:
                function_path_and_name = extract_package_path(query)
                if function_path_and_name:
                    function_info = get_function_info(
                        function_path_and_name, add_docstrings=add_docstrings
                    )

                    if len(function_info) > 512:
                        function_info = summarize(function_info)
                        result = f"Here is the summarised information you requested about function {function_path_and_name}:\n{function_info}\n"
                    else:
                        result = f"Here is the full information including docstrings you requested about function {function_path_and_name}:\n{function_info}\n"

                else:
                    result = (
                        "Error: there is no qualified function name in the request!"
                    )

                aprint(result)
                return result

            except Exception as e:
                error_info = f"Error: {type(e).__name__} with message: '{str(e)}' occurred while trying to get information about: '{function_path_and_name}'."
                traceback.print_exc()
                return error_info
