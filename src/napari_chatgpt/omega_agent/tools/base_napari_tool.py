import sys
import traceback
from pathlib import Path
from queue import Queue
from typing import Optional, Any

from arbol import aprint, asection
from napari import Viewer

from napari_chatgpt.llm.llm import LLM
from napari_chatgpt.omega_agent.napari_bridge import _get_viewer_info
from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool
from napari_chatgpt.omega_agent.tools.generic_coding_instructions import (
    omega_generic_codegen_instructions,
)
from napari_chatgpt.utils.notebook.jupyter_notebook import JupyterNotebookFile
from napari_chatgpt.utils.python.consolidate_imports import consolidate_imports
from napari_chatgpt.utils.python.dynamic_import import execute_as_module
from napari_chatgpt.utils.python.exception_description import exception_description
from napari_chatgpt.utils.python.exception_guard import ExceptionGuard
from napari_chatgpt.utils.python.fix_bad_fun_calls import fix_all_bad_function_calls
from napari_chatgpt.utils.python.fix_code_given_error import (
    fix_code_given_error_message,
)
from napari_chatgpt.utils.python.installed_packages import installed_package_list
from napari_chatgpt.utils.python.missing_packages import required_packages
from napari_chatgpt.utils.python.pip_utils import pip_install
from napari_chatgpt.utils.python.required_imports import required_imports
from napari_chatgpt.utils.strings.extract_code import extract_code_from_markdown
from napari_chatgpt.utils.strings.filter_lines import filter_lines
from napari_chatgpt.utils.system.information import system_info


class BaseNapariTool(BaseOmegaTool):
    """
    A base tool that delegates to execution to a sub-LLM and communicates with napari via queues.
    This tool is designed to generate and execute Python code in the napari environment.
    It can be used to create widgets, run code, and interact with the napari viewer.
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
        fix_imports: bool = True,
        install_missing_packages: bool = True,
        fix_bad_calls: bool = False,
        verbose: bool = False,
        notebook: Optional[JupyterNotebookFile] = None,
        last_generated_code: Optional[str] = None,
        **kwargs: dict,
    ):
        """
        Initialize a BaseNapariTool instance for generating and executing Python code in the napari environment.
        
        This constructor sets up tool identity, code generation parameters, communication queues, LLM integration, and various behavior flags. It also prepares optional notebook integration and caches the list of installed packages for use in code preparation and execution.
        
        Parameters:
            name (str): Unique name for the tool.
            description (str): Unique description of the tool's purpose.
            code_prefix (str): Code to prepend to generated code, such as imports.
            instructions (str): Instructions to guide the sub-LLM's code generation.
            prompt (str, optional): Prompt for the sub-LLM; if None, code generation is not delegated.
            return_direct (bool): If True, returns generated code directly instead of sending to napari.
            save_last_generated_code (bool): If True, caches the last generated code for future reference.
            fix_imports (bool): If True, attempts to fix missing imports in generated code.
            install_missing_packages (bool): If True, attempts to install required but missing packages.
            fix_bad_calls (bool): If True, attempts to fix invalid function calls in generated code.
            verbose (bool): If True, enables verbose logging.
            last_generated_code (str, optional): Previously generated code for prompt context.
            notebook (JupyterNotebookFile, optional): Optional notebook integration.
            **kwargs: Additional keyword arguments for extensibility.
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
        self.fix_imports = fix_imports
        self.install_missing_packages = install_missing_packages
        self.fix_bad_calls = fix_bad_calls
        self.verbose = verbose
        self.last_generated_code = last_generated_code

        self.notebook = notebook

        self._installed_package_list = installed_package_list()

    def run_omega_tool(self, query: str = "") -> Any:
        """
        Generates Python code using a sub-LLM based on the provided query and tool instructions, sends the code for execution in the napari environment, and returns the execution result or an error message.
        
        If a prompt is configured, this method prepares a context-rich prompt for the LLM, including previous code, environment details, and instructions. The generated code is sent to napari for execution via a delegated function and communication queues. The method returns the result from napari, or an error message if execution fails.
        
        Parameters:
            query (str): The user query or instruction for code generation.
        
        Returns:
            Any: The result of code execution in napari, or an error message string if execution fails.
        """

        if self.prompt:
            # Instantiate message

            if self.last_generated_code:
                last_generated_code = ("**Previously Generated Code:**\n",)
                last_generated_code += (
                    "Use this code for reference, usefull if you need to modify or fix the code. ",
                    "IMPORTANT: This code might not be relevant to the current request or task! "
                    "You should ignore it, unless you are explicitely asked to fix or modify the last generated widget!",
                    "```python\n",
                    self.last_generated_code + "\n",
                    "```\n",
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
        """
        Executes the provided code in the napari viewer context.
        
        This method must be implemented by subclasses to define how code is executed. It should return a string beginning with 'Success:' if execution is successful; otherwise, it should indicate failure.
        """
        raise NotImplementedError("This method must be implemented")

    def _prepare_code(
        self,
        code: str,
        markdown: bool = True,
        do_fix_imports: bool = True,
        do_fix_bad_calls: bool = True,
        do_install_missing_packages: bool = True,
    ) -> str:

        """
        Prepare and sanitize Python code for execution in the napari environment.
        
        This method extracts code from markdown if needed, prepends a code prefix, fixes missing imports and bad function calls, removes disallowed lines related to napari viewer instantiation or GUI manipulation, and installs any required but missing packages. The resulting code is returned as a ready-to-execute string.
        
        Parameters:
            code (str): The Python code to prepare.
            markdown (bool): Whether to extract code from markdown format.
            do_fix_imports (bool): Whether to detect and add missing imports.
            do_fix_bad_calls (bool): Whether to fix bad function calls in the code.
            do_install_missing_packages (bool): Whether to detect and install missing packages.
        
        Returns:
            str: The fully prepared and sanitized Python code.
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

            if self.fix_imports and do_fix_imports:
                # Are there any missing imports?
                imports = required_imports(code, llm=self.llm)

                # prepend missing imports:
                code = "\n".join(imports) + "\n\n" + code

                # consolidate imports:
                code = consolidate_imports(code)

                # notify that code was modified for missing imports:
                code = "# Note: code was modified to add missing imports:\n" + code

            # Fix code, this takes care of wrong function calls and more:
            if self.fix_bad_calls and do_fix_bad_calls:
                code, fixed, _ = fix_all_bad_function_calls(code)

                if fixed:
                    # notify that code was fixed for bad calls:
                    code = (
                        "# Note: code was modified to fix bad function calls.\n" + code
                    )

            # Remove any offending lines:
            code = filter_lines(
                code,
                [
                    "napari.Viewer(",
                    "= Viewer(",
                    "gui_qt(",
                    "viewer.window.add_dock_widget(",
                ],
            )

            with asection(f"code after all preparations and fixes:"):
                aprint(code)

            if self.install_missing_packages and do_install_missing_packages:
                # Are there missing libraries that need to be installed?
                packages = required_packages(code, llm=self.llm)

                # Install them:
                pip_install(packages)

                # Notify that some packages might be missing and that Omega attempted to install them:
                code = (
                    f"# Note: some packages ({','.join(packages)}) might be missing and Omega attempted to install them.\n"
                    + code
                )

            # Return fully prepared and fixed code:
            return code

    def _run_code_catch_errors_fix_and_try_again(
        self, code, viewer, error: str = "", instructions: str = "", nb_tries: int = 3
    ) -> str:

        """
        Attempts to execute the provided code in the napari viewer context, automatically fixing errors and retrying execution up to a specified number of times.
        
        If execution fails, the method uses the LLM to attempt to fix the code based on the encountered error and retries until successful or the retry limit is reached. On success, the executed code is added to the microplugin code snippet editor and, if available, to a Jupyter notebook.
        
        Parameters:
            code (str): The Python code to execute.
            viewer (Viewer): The napari viewer instance in which to execute the code.
            error (str, optional): Additional error context to provide to the code fixer.
            instructions (str, optional): Extra instructions for the code fixer.
            nb_tries (int, optional): Maximum number of attempts to execute and fix the code.
        
        Returns:
            str: The output captured from the successful code execution.
        
        Raises:
            Exception: If all retry attempts fail, the last encountered exception is raised.
        """
        try:
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

        except Exception as e:
            if nb_tries >= 1:
                traceback.print_exc()
                description = error + "\n\n" + exception_description(e)
                description = description.strip()
                fixed_code = fix_code_given_error_message(
                    code=code,
                    error=description,
                    instructions=instructions,
                    viewer=viewer,
                    llm=self.llm,
                    verbose=self.verbose,
                )
                # We try again:
                return self._run_code_catch_errors_fix_and_try_again(
                    fixed_code, viewer=viewer, error=error, nb_tries=nb_tries - 1
                )
            else:
                # No more tries available, we give up!
                raise e

        return captured_output


def _get_delegated_code(name: str, signature: bool = False):
    """
    Retrieve the contents of a delegated Python code file by name, optionally extracting only the signature section.
    
    Parameters:
        name (str): The base name of the delegated code file (without extension).
        signature (bool): If True, returns only the code section after the '### SIGNATURE' marker.
    
    Returns:
        str: The full code or the signature section from the specified delegated code file.
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
