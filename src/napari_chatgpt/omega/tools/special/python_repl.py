import ast
import re
import sys
from contextlib import redirect_stdout
from io import StringIO
from typing import Dict, Optional

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.utilities import PythonREPL
from pydantic import Field, root_validator

from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool


def _get_default_python_repl() -> PythonREPL:
    return PythonREPL(_globals=globals(), _locals=None)


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
        "Use this tool to execute python code and commands that do not involve to the napari. "
        "Do not use this tool to have access to napari or its viewer. "
        "This tool is not suitable for image processing, analysis or visualisation. "
        "Input should be a valid python command. "
        "For example, send: `print(3**1+1)` to get the result of this calculation thescipy.ndimage.convolve and this tool will returns the full signature of this function "
        "If you want to see the output of a value, you should print it out with `print(...)`."
    )

    globals: Optional[Dict] = Field(default_factory=dict)
    locals: Optional[Dict] = Field(default_factory=dict)
    sanitize_input: bool = True

    @root_validator(pre=True)
    def validate_python_version(cls, values: Dict) -> Dict:
        """Validate valid python version."""
        if sys.version_info < (3, 9):
            raise ValueError(
                "This tool relies on Python 3.9 or higher "
                "(as it uses new functionality in the `ast` module, "
                f"you have Python version: {sys.version}"
            )
        return values

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
