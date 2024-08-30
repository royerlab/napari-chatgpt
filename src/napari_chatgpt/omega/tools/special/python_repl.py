import ast
import re
from contextlib import redirect_stdout
from io import StringIO
from typing import Dict, Optional, Any

from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool


class PythonCodeExecutionTool(AsyncBaseTool):
    """A tool for running non-napari-related python code in a REPL."""

    name = "PythonCodeExecutionTool"
    description = (
        "Use this tool *sparingly* to execute very short snippets of python code. "
        "Do *not* use this tool to access to the napari viewer or its layers. "
        "Do *not* use this tool to work on images, videos, large nD arrays, or other large datasets. "
        "Input should be a *very short* and valid python command, ideally a print statement."
        "For example, send: `print(3**3+1)` to get the result of this calculation which is 28. "
        "If you want to see the output, you should print it out with `print(...)`."
    )

    sanitize_input: bool = True

    def _run(
        self,
        *args: Any,
        **kwargs: Any
    ) -> Any:

        try:
            _globals = globals()
            _locals = locals()

            # Get query:
            query = self.normalise_to_string(kwargs)

            # Sanitize input:
            if self.sanitize_input:
                query = sanitize_input(query)

            # add code cell to notebook if available:
            if self.notebook:
                self.notebook.add_code_cell(query)

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
        except Exception as e:
            return "{}: {}".format(type(e).__name__, str(e))


def sanitize_input(query: str) -> str:
    # Remove whitespace, backtick & python (if llm mistakes python console as terminal)

    # Removes `, whitespace & python from start
    query = re.sub(r"^(\s|`)*(?i:python)?\s*", "", query)
    # Removes whitespace & ` from end
    query = re.sub(r"(\s|`)*$", "", query)
    return query