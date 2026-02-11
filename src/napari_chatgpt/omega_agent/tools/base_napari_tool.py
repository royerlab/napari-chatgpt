"""Base class for napari-aware Omega tools that generate and execute code.

Provides ``BaseNapariTool``, which delegates code generation to a sub-LLM,
sends the resulting callable to the napari Qt thread via queues, and
collects the execution result. Concrete subclasses override ``_run_code``
to define tool-specific execution logic.
"""

import sys
from pathlib import Path
from queue import Queue
from typing import Any

from arbol import aprint, asection
from napari import Viewer

from napari_chatgpt.llm.llm import LLM
from napari_chatgpt.omega_agent.napari_bridge import _get_viewer_info
from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool
from napari_chatgpt.omega_agent.tools.generic_coding_instructions import (
    omega_generic_codegen_instructions,
)
from napari_chatgpt.utils.notebook.jupyter_notebook import JupyterNotebookFile
from napari_chatgpt.utils.python.dynamic_import import execute_as_module
from napari_chatgpt.utils.python.exception_guard import ExceptionGuard
from napari_chatgpt.utils.python.installed_packages import installed_package_list
from napari_chatgpt.utils.strings.extract_code import extract_code_from_markdown
from napari_chatgpt.utils.strings.filter_lines import filter_lines
from napari_chatgpt.utils.system.information import system_info


class BaseNapariTool(BaseOmegaTool):
    """Base tool that delegates code generation to a sub-LLM and executes it in napari.

    The typical lifecycle is:

    1. ``run_omega_tool`` formats a prompt with viewer state and sends it to
       the sub-LLM, which returns Python code.
    2. The code is wrapped in a callable and placed on ``to_napari_queue``.
    3. The Qt-side worker executes the callable and puts the result on
       ``from_napari_queue``.
    4. The result (or error) is returned to the calling agent.

    Subclasses must implement ``_run_code`` to define how the generated
    code is prepared and executed.
    """

    def __init__(
        self,
        name: str = "<NAME>",
        description: str = "Enter Description Here",
        code_prefix: str = "",
        instructions: str = omega_generic_codegen_instructions,
        prompt: str = None,
        to_napari_queue: Queue = None,
        from_napari_queue: Queue = None,
        llm: LLM = None,
        return_direct: bool = False,
        save_last_generated_code: bool = True,
        verbose: bool = False,
        notebook: JupyterNotebookFile | None = None,
        last_generated_code: str | None = None,
        **kwargs: dict,
    ):
        """Initialise the napari tool.

        Args:
            name: Unique tool name.
            description: Human-readable tool description.
            code_prefix: Python code prepended to every generated
                snippet (e.g. common imports).
            instructions: Coding instructions appended to the generic
                code-generation guidelines for the sub-LLM.
            prompt: Prompt template for the sub-LLM. If ``None``, no
                LLM delegation occurs and ``_run_code`` receives
                ``code=None``.
            to_napari_queue: Queue for sending callables to napari's Qt
                thread.
            from_napari_queue: Queue for receiving execution results
                from napari's Qt thread.
            llm: LLM instance used for code generation.
            return_direct: If ``True``, the tool returns the raw LLM
                output without executing it.
            save_last_generated_code: If ``True``, persist the most
                recent generated code for reference in subsequent calls.
            verbose: Enable verbose logging.
            notebook: Optional Jupyter notebook to record generated code.
            last_generated_code: Seed value for previously generated
                code, if any.
            **kwargs: Extra keyword arguments (forwarded to parent).
        """

        super().__init__(name=name, description=description, **kwargs)

        self.code_prefix = code_prefix
        self.instructions = instructions
        self.prompt = prompt
        self.to_napari_queue = to_napari_queue
        self.from_napari_queue = from_napari_queue
        self.llm = llm
        self.return_direct = return_direct
        self.save_last_generated_code = save_last_generated_code
        self.verbose = verbose
        self.last_generated_code = last_generated_code

        self.notebook = notebook

        self._installed_package_list = installed_package_list()

    def run_omega_tool(self, query: str = "") -> Any:
        """Generate code via the sub-LLM and execute it in napari.

        Args:
            query: The user request or task description.

        Returns:
            A success/result string from ``_run_code``, or an error
            message if execution raised an exception.
        """

        if self.prompt:
            # Instantiate message

            if self.last_generated_code:
                last_generated_code = (
                    "**Previously Generated Code:**\n"
                    "Use this code for reference, useful if you need to modify or fix the code. "
                    "IMPORTANT: This code might not be relevant to the current request or task! "
                    "You should ignore it, unless you are explicitly asked to fix or modify the last generated widget!\n"
                    "```python\n" + self.last_generated_code + "\n"
                    "```\n"
                )
            else:
                last_generated_code = ""

            # Adding information about packages and Python version to instructions:
            filled_generic_instructions = omega_generic_codegen_instructions.format(
                python_version=str(sys.version.split()[0]),
                packages=", ".join(self._installed_package_list),
            )

            # Prepend generic instructions to tool specific instructions:
            instructions = filled_generic_instructions + self.instructions

            # Variable for prompt:
            variables = {
                "input": query,
                "instructions": instructions,
                "last_generated_code": last_generated_code,
                "viewer_information": "For reference, below is information about the current state of the napari viewer: \n"
                + _get_viewer_info(),
                "system_information": "For reference, below is information about the current system: \n"
                + system_info(add_python_info=False),
            }

            # call LLM:
            result = self.llm.generate(
                prompt=self.prompt,
                # system='',
                variables=variables,
            )

            # Get code from result:
            code = "\n\n".join([m.to_plain_text() for m in result])

            aprint(f"code:\n{code}")
        else:
            # No code generated because no sub-LLM delegation, delegated_function has the business logic.
            code = None

        # Update last generated code:
        if self.save_last_generated_code:
            self.last_generated_code = code

        # Setting up delegated function:
        delegated_function = lambda v: self._run_code(query, code, v)

        # Send code to napari:
        self.to_napari_queue.put(delegated_function)

        # Get response:
        response = self.from_napari_queue.get()

        if isinstance(response, ExceptionGuard):
            exception_guard = response
            # raise exception_guard.exception
            return f"Error: {exception_guard.exception_type_name} with message: '{str(exception_guard.exception)}' while using tool: {self.__class__.__name__} ."

        return response

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:
        """Execute tool-specific logic on the Qt thread.

        Subclasses must override this method. The return value should
        start with ``'Success: ...'`` on success; any other value is
        treated as a failure by the agent.

        Args:
            query: The original user request.
            code: The Python code generated by the sub-LLM, or ``None``
                if no LLM delegation was configured.
            viewer: The napari ``Viewer`` instance.

        Returns:
            A result string describing the outcome.

        Raises:
            NotImplementedError: Always, unless overridden.
        """
        raise NotImplementedError("This method must be implemented")

    def _prepare_code(
        self,
        code: str,
        markdown: bool = True,
    ) -> str:
        """Sanitise and prepare LLM-generated code for execution.

        Strips Markdown fences, prepends the tool's ``code_prefix``,
        and removes lines that would interfere with the existing napari
        session (e.g. creating a new viewer or calling ``gui_qt``).

        Args:
            code: Raw code string, possibly wrapped in Markdown fences.
            markdown: If ``True``, extract code from Markdown code
                blocks first.

        Returns:
            The cleaned Python source ready for execution.
        """

        with asection(f"NapariBaseTool: _prepare_code(markdown={markdown}) "):

            with asection(f"code to prepare:"):
                aprint(code)

            # extract code from markdown:
            if markdown:
                code = extract_code_from_markdown(code)

            # Prepend prefix:
            code = self.code_prefix + code

            # Add spaces around code:
            code = "\n\n" + code + "\n\n"

            # Remove any offending lines:
            code = filter_lines(
                code,
                [
                    "from __future__",
                    "napari.Viewer(",
                    "= Viewer(",
                    "gui_qt(",
                    "viewer.window.add_dock_widget(",
                ],
            )

            with asection(f"code after all preparations:"):
                aprint(code)

            return code

    def _execute_code(self, code, viewer) -> str:
        """Execute prepared Python code in the context of the napari viewer.

        After successful execution the code is saved to the MicroPlugin
        snippet editor and, if a notebook is configured, appended as a
        code cell.

        Args:
            code: Python source code to execute.
            viewer: The napari ``Viewer`` instance available as
                ``viewer`` inside the executed code.

        Returns:
            The captured ``stdout`` output from the executed code.
        """

        with asection(f"Running code:"):

            # Run the code:
            aprint(f"Code:\n{code}")
            captured_output = execute_as_module(code, viewer=viewer)

            # Call the activity callback. At this point we assume the code is correct because it ran!
            self.callbacks.on_tool_activity(self, "coding", code=code)

            # Come up with a filename:
            filename = f"generated_code_{self.__class__.__name__}.py"

            # Add the snippet to the code snippet editor:
            from napari_chatgpt.microplugin.microplugin_window import (
                MicroPluginMainWindow,
            )

            MicroPluginMainWindow.add_snippet(filename=filename, code=code)

            # Add successfully run code to notebook:
            if self.notebook:
                self.notebook.add_code_cell(code)
            aprint(f"This is what the code returned:\n{captured_output}")

        return captured_output


def _get_delegated_code(name: str, signature: bool = False):
    """Load a delegated code template from the ``napari/delegated_code`` directory.

    Args:
        name: Stem of the ``.py`` file to load (without extension).
        signature: If ``True``, return only the portion of the file
            after the ``### SIGNATURE`` marker.

    Returns:
        The file contents (or the signature portion) as a string.
    """
    with asection(f"Getting delegated code: '{name}' (signature={signature})"):
        # Get current package folder:
        current_package_folder = Path(__file__).parent

        # Get package folder:
        package_folder = Path.joinpath(current_package_folder, f"napari/delegated_code")

        # file path:
        file_path = Path.joinpath(package_folder, f"{name}.py")
        aprint(f"Filepath: {file_path}")

        # code:
        code = file_path.read_text()

        # extract signature:
        if signature:
            aprint("Extracting signature!")
            splitted_code = code.split("### SIGNATURE")
            code = splitted_code[1]

        return code
