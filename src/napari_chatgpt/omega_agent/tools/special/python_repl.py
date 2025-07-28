import ast
import re
from contextlib import redirect_stdout
from io import StringIO

from arbol import asection, aprint

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool


class PythonCodeExecutionTool(BaseOmegaTool):
    """
    A tool for running non-napari-related python code in a REPL.
    This tool can be used to execute very short snippets of python code.
    """

    def __init__(self, **kwargs):
        """
        Initialize the PythonCodeExecutionTool with default settings for executing short Python code snippets.
        
        Sets the tool's name, usage description, and enables input sanitization by default.
        """
        super().__init__(**kwargs)

        self.name = "PythonCodeExecutionTool"
        self.description = (
            "Use this tool *sparingly* to execute very short snippets of python code. "
            "Do *not* use this tool to access to the napari viewer or its layers. "
            "Do *not* use this tool to work on images, videos, large nD arrays, or other large datasets. "
            "Input should be a *very short* and valid python command, ideally a print statement."
            "For example, send: `print(3**3+1)` to get the result of this calculation which is 28. "
            "If you want to see the output, you should print it out with `print(...)`."
        )

        self.sanitize_input: bool = True

    def run_omega_tool(self, query: str = ""):
        """
        Executes a short Python code snippet in a controlled REPL-like environment and returns its output or result.
        
        If the input contains multiple statements, all but the last are executed, and the last is evaluated or executed to capture its output or return value. Printed output is captured and returned if no value is produced. Input can be sanitized to remove extraneous formatting. Any exceptions during parsing or execution are caught and returned as error messages.
        
        Parameters:
            query (str): The Python code snippet to execute.
        
        Returns:
            The result of the last statement if it produces a value, the captured printed output, or an error message if execution fails.
        """
        with asection(f"PythonCodeExecutionTool:"):
            with asection(f"Query:"):
                aprint(query)

            try:
                _globals = globals()
                _locals = locals()

                # Sanitize input:
                if self.sanitize_input:
                    query = sanitize_input(query)

                # Parse and execute the code:
                tree = ast.parse(query)
                module = ast.Module(tree.body[:-1], type_ignores=[])
                exec(ast.unparse(module), _globals, _locals)  # type: ignore
                module_end = ast.Module(tree.body[-1:], type_ignores=[])
                module_end_str = ast.unparse(module_end)  # type: ignore
                io_buffer = StringIO()
                try:
                    with redirect_stdout(io_buffer):
                        ret = eval(module_end_str, _globals, _locals)
                        if ret is None:
                            return io_buffer.getvalue()
                        else:
                            return ret

                except Exception:
                    with redirect_stdout(io_buffer):
                        exec(module_end_str, _globals, _locals)
                    return io_buffer.getvalue()

                # Call the activity callback. At this point we assume the code is correct because it ran!
                self.callbacks.on_tool_activity(self, "coding", code=code)

                # add code cell to notebook if available:
                if self.notebook:
                    self.notebook.add_code_cell(query)

            except Exception as e:
                return "{}: {}".format(type(e).__name__, str(e))


def sanitize_input(query: str) -> str:
    # Remove whitespace, backtick & python (if llm mistakes python console as terminal)

    # Removes `, whitespace & python from start
    """
    Sanitize a Python code snippet by removing leading/trailing whitespace, backticks, and an optional 'python' prefix.
    
    Parameters:
        query (str): The input code snippet to sanitize.
    
    Returns:
        str: The cleaned code snippet ready for execution.
    """
    query = re.sub(r"^(\s|`)*(?i:python)?\s*", "", query)
    # Removes whitespace & ` from end
    query = re.sub(r"(\s|`)*$", "", query)
    return query
