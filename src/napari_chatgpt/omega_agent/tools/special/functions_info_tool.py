"""Tool for querying signatures and docstrings of Python functions.

Given a fully qualified function name (e.g., ``scipy.ndimage.convolve``),
this tool imports the function and returns its signature with type hints.
Prefixing the query with ``*`` also includes the full docstring.
"""

import traceback

from arbol import aprint, asection

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool
from napari_chatgpt.utils.python.python_lang_utils import (
    extract_package_path,
    get_function_info,
)

_MAX_RESULT_LENGTH = 4096


class PythonFunctionsInfoTool(BaseOmegaTool):
    """Tool for retrieving Python function signatures and docstrings.

    Accepts a fully qualified function name, imports it, and returns
    its signature (with type hints when available). If the query is
    prefixed with ``*``, the full docstring is included as well. Results
    longer than ``_MAX_RESULT_LENGTH`` characters are truncated.

    Attributes:
        name: Tool identifier string.
        description: Human-readable description used by the LLM agent.
    """

    def __init__(self, **kwargs):
        """Initialize the PythonFunctionsInfoTool.

        Args:
            **kwargs: Keyword arguments forwarded to ``BaseOmegaTool``.
        """
        super().__init__(**kwargs)

        self.name = "PythonFunctionsInfoTool"
        self.description = (
            "Use this tool for querying the signature and docstrings of "
            "python and library functions from their fully qualified name. "
            "For example, send: 'scipy.ndimage.convolve' and this tool "
            "will return the full signature of this function "
            "with all its parameters and if possible corresponding "
            "type hints. "
            "You can use this tool to check the correct signature of "
            "functions before writing python code, or when errors are "
            "encountered. "
            "If you want the whole docstring to get a better "
            "understanding of the function, its parameters, "
            "and example usages, please prefix your request with "
            "the single star character '*'."
        )

    def run_omega_tool(self, query: str = ""):
        """Look up and return the signature (and optionally docstring) of a function.

        Args:
            query: Fully qualified function name (e.g., ``'numpy.mean'``).
                Prefix with ``*`` to include the full docstring.

        Returns:
            A string containing the function signature and optional
            docstring, or an error message if the function cannot be found.
        """
        with asection("PythonFunctionsInfoTool:"):
            with asection("Query:"):
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
                        function_path_and_name,
                        add_docstrings=add_docstrings,
                    )

                    # Truncate if too long instead of calling LLM:
                    if len(function_info) > _MAX_RESULT_LENGTH:
                        function_info = (
                            function_info[:_MAX_RESULT_LENGTH] + "\n... (truncated)"
                        )

                    result = (
                        f"Here is the information about function "
                        f"{function_path_and_name}:\n"
                        f"{function_info}\n"
                    )

                else:
                    result = (
                        "Error: no qualified function name" " found in the request!"
                    )

                aprint(result)
                return result

            except Exception as e:
                error_info = (
                    f"Error: {type(e).__name__} with message: "
                    f"'{str(e)}' occurred while trying to get "
                    f"information about: "
                    f"'{function_path_and_name}'."
                )
                traceback.print_exc()
                return error_info
