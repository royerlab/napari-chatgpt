"""Tool for executing short Python code snippets in a sandboxed REPL.

Provides the Omega agent with a lightweight Python REPL for quick
computations and queries that do not involve the napari viewer or large
datasets. Code is parsed via ``ast``, sanitized, and executed; stdout
output (or the return value of the last expression) is captured and
returned to the agent.
"""

import ast
import re
from contextlib import redirect_stdout
from io import StringIO

from arbol import aprint, asection

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool


class PythonCodeExecutionTool(BaseOmegaTool):
    """Tool for running short Python snippets in a REPL environment.

    Parses the input as Python source, executes all statements except the
    last, then evaluates (or executes) the last statement and captures its
    output. Not intended for napari-related or heavy data processing code.

    Attributes:
        name: Tool identifier string.
        description: Human-readable description used by the LLM agent.
        sanitize_input: Whether to strip backticks and language markers
            from the input before execution.
    """

    def __init__(self, **kwargs):
        """Initialize the PythonCodeExecutionTool.

        Args:
            **kwargs: Keyword arguments forwarded to ``BaseOmegaTool``,
                including an optional ``notebook`` for logging code cells.
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
        """Execute a short Python code snippet and return the output.

        The code is optionally sanitized (backticks and ``python`` markers
        removed), parsed into an AST, and executed. All statements except
        the last are executed for side effects; the last statement is
        evaluated and its result (or captured stdout) is returned.

        Args:
            query: Python source code to execute.

        Returns:
            The string representation of the result of the last expression,
            captured stdout output, or an error message on failure.
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
                        output = io_buffer.getvalue() if ret is None else ret
                except Exception:
                    with redirect_stdout(io_buffer):
                        exec(module_end_str, _globals, _locals)
                    output = io_buffer.getvalue()

                # Call the activity callback. At this point we assume the code is correct because it ran!
                self.callbacks.on_tool_activity(self, "coding", code=query)

                # add code cell to notebook if available:
                if self.notebook:
                    self.notebook.add_code_cell(query)

                return output

            except Exception as e:
                return f"{type(e).__name__}: {str(e)}"


def sanitize_input(query: str) -> str:
    """Strip markdown code-fence artifacts from a Python code string.

    Removes leading/trailing backticks, whitespace, and an optional
    ``python`` language identifier that LLMs sometimes include when
    formatting code as a markdown fenced block.

    Args:
        query: Raw code string potentially wrapped in markdown backticks.

    Returns:
        Cleaned Python source code ready for execution.
    """
    # Removes `, whitespace & python from start
    query = re.sub(r"^(\s|`)*(?i:python)?\s*", "", query)
    # Removes whitespace & ` from end
    query = re.sub(r"(\s|`)*$", "", query)
    return query
