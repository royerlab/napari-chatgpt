import ast
import re
from contextlib import redirect_stdout
from io import StringIO
from typing import Dict, Optional

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from pydantic import Field

from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool


def sanitize_input(query: str) -> str:
    # Remove whitespace, backtick & python (if llm mistakes python console as terminal)

    # Removes `, whitespace & python from start
    query = re.sub(r"^(\s|`)*(?i:python)?\s*", "", query)
    # Removes whitespace & ` from end
    query = re.sub(r"(\s|`)*$", "", query)
    return query


class PythonCodeExecutionTool(AsyncBaseTool):
    """A tool for running non-napari-related python code in a REPL."""

    name = "PythonCodeExecutionTool"
    description = (
        "Use this tool to execute short snippets of python code unrelated to images. "
        "Do not use this tool if you need access to the napari viewer or its layers: instead use the napari viewer query, control or execution tools. "
        "This tool is absolutely *not* suitable for generating, processing, analysing or visualising images, videos, large nD arrays, or other large datasets. "
        "Input should be a short and valid python command. "
        "For example, send: `print(3**3+1)` to get the result of this calculation which is 28. "
        "If you want to see the output, you should print it out with `print(...)`."
    )

    globals: Optional[Dict] = Field(default_factory=dict)
    locals: Optional[Dict] = Field(default_factory=dict)
    sanitize_input: bool = True

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        try:
            if self.sanitize_input:
                query = sanitize_input(query)

            if self.notebook:
                self.notebook.add_code_cell(query)

            tree = ast.parse(query)
            module = ast.Module(tree.body[:-1], type_ignores=[])
            exec(ast.unparse(module), self.globals, self.locals)  # type: ignore
            module_end = ast.Module(tree.body[-1:], type_ignores=[])
            module_end_str = ast.unparse(module_end)  # type: ignore
            io_buffer = StringIO()
            try:
                with redirect_stdout(io_buffer):
                    ret = eval(module_end_str, self.globals, self.locals)
                    if ret is None:
                        return io_buffer.getvalue()
                    else:
                        return ret
            except Exception:
                with redirect_stdout(io_buffer):
                    exec(module_end_str, self.globals, self.locals)
                return io_buffer.getvalue()
        except Exception as e:
            return "{}: {}".format(type(e).__name__, str(e))
