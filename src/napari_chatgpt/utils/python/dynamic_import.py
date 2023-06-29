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
    if not name:
        name = f'some_code_{randint(0, 999999999)}'

    # Write code to temp file:
    with tempfile.NamedTemporaryFile(mode="w", suffix='.py', delete=False) as f:
        f.write(module_code)
        module_path = f.name

    # Load the module from the temporary file
    spec = importlib.util.spec_from_file_location(name=name,
                                                  location=module_path)

    # Not clear what this is about:
    loaded_module = importlib.util.module_from_spec(spec)

    # Execute module:
    spec.loader.exec_module(loaded_module)

    return loaded_module





def execute_as_module(code_str, name: str = None, **kwargs) -> str:

    with asection(f"Executing code as module (length={code_str})"):

        # Create a function in the new module that will receive the variables
        # as arguments, and will contain the code_str
        module_code = \
"""
def execute_code({}):
{}
""".format(
    ', '.join(kwargs.keys()) if kwargs else "",
    '\n'.join('\t' + i for i in code_str.split('\n'))
    # indent the code_str
            )

        with asection(f"Module code:"):
            aprint(module_code)

        # Load the code as module:
        module = dynamic_import(module_code, name)

        # get the function from module:
        execute_code = getattr(module, 'execute_code')

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



