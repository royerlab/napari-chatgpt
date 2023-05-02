"""A tool for running python code in a REPL."""
import traceback

from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool
from napari_chatgpt.utils.inspection import extract_package_path, \
    get_function_info
from napari_chatgpt.utils.summarizer import summarize


class PythonFunctionsInfoTool(AsyncBaseTool):
    """A tool for querying the signature and docstrings of python functions."""

    name = "PythonFunctionsInfoTool"
    description = (
        "A tool for querying the signature and docstrings of python functions from their fully qualified name. "
        "For example, send: scipy.ndimage.convolve and this tool will returns the full signature of this function "
        "with all its parameters and if possible corresponding type hints. "
        "You can use this tool to check the correct signature of functions before writting python code. "
        "If you want the whole docstring to get a better understanding of the function, its parameters, "
        "and example usages, please prefix your request with the single star character '*'."
    )

    def _run(self, query: str) -> str:
        """Use the tool."""

        add_docstrings = False

        if '*' in query:
            query = query.replace('*', '')
            add_docstrings = True

        try:
            function_path_and_name = extract_package_path(query)
            if function_path_and_name:
                function_info = get_function_info(function_path_and_name,
                                                  add_docstrings=add_docstrings)

                if len(function_info) > 512:
                    function_info = summarize(function_info)

                result = f"Here is the information you requested about function {function_path_and_name}:\n{function_info}\n"
                return result
            else:
                return "Error: there is no qualified function name in the request!"

        except Exception as e:
            error_info = f"Error: {type(e).__name__} occured while trying to get information about: '{function_path_and_name}'."
            traceback.print_exc()
            return error_info
