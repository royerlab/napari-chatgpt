import importlib.util
import tempfile
from typing import Optional, Any


def dynamic_import(module_code: str) -> Optional[Any]:
    # Write code to temp file:
    with tempfile.NamedTemporaryFile(mode="w", suffix='.py', delete=False) as f:
        f.write(module_code)
        module_path = f.name

    # Load the module from the temporary file
    spec = importlib.util.spec_from_file_location("some_code", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module
