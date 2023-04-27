import importlib.util
import tempfile
from random import randint
from typing import Optional, Any


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
