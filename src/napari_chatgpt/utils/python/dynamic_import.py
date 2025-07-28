import importlib.util
import importlib.util
import tempfile
from contextlib import redirect_stdout
from io import StringIO
from random import randint
from typing import Optional, Any

from arbol import asection, aprint


def dynamic_import(module_code: str, name: str = None) -> Optional[Any]:
    # Module name:
    """
    Dynamically imports a Python module from a source code string.
    
    If no module name is provided, a random name is generated. The code is written to a temporary file, loaded as a module, and executed. Returns the loaded module object.
    """
    if not name:
        name = f"some_code_{randint(0, 999999999)}"

    # Write code to temp file:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(module_code)
        module_path = f.name

    # Load the module from the temporary file
    spec = importlib.util.spec_from_file_location(name=name, location=module_path)

    # Not clear what this is about:
    loaded_module = importlib.util.module_from_spec(spec)

    # Execute module:
    spec.loader.exec_module(loaded_module)

    return loaded_module


# This should not have spurious whitespace, as it is used to format the code:
__execution_harness =\
"""
def execute_code({}):
{}
"""


def execute_as_module(code_str, name: str = None, **kwargs) -> str:
    """
    Execute a code string as a dynamically created module function with optional input variables and capture its standard output.
    
    Parameters:
        code_str (str): The Python code to execute as the body of a function.
        name (str, optional): The name to assign to the generated module.
        **kwargs: Variables to pass as arguments to the executed function.
    
    Returns:
        str: The captured standard output produced by the executed code.
    """
    with asection(f"Executing code as module (length={len(code_str)})"):

        # Create a function in the new module that will receive the variables
        # as arguments, and will contain the code_str

        # prepare the arguments and code strings:
        arguments_str = ", ".join(kwargs.keys()) if kwargs else ""
        code_str = "\n".join("\t" + i for i in code_str.split("\n"))

        # Format the final module code
        module_code = __execution_harness.format(arguments_str, code_str)

        with asection(f"Module code:"):
            aprint(module_code)

        # Load the code as module:
        _module_ = dynamic_import(module_code, name)

        # get the function from module:
        execute_code = getattr(_module_, "execute_code")

        f = StringIO()
        with redirect_stdout(f):
            # Call the execute_code function with the global variables as arguments
            if kwargs:
                execute_code(**kwargs)
            else:
                execute_code()

        # Get captured stdout:
        captured_output = f.getvalue().strip()

        return captured_output
