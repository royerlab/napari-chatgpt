"""Python introspection and function discovery utilities.

Provides functions for inspecting Python objects at runtime, including
retrieving function signatures, docstrings, and type hints; extracting
fully qualified function names from source code via AST parsing; and
searching packages for functions by name.
"""

import ast
import importlib
import inspect
import re
import traceback
from functools import lru_cache
from typing import Any, get_type_hints

from arbol import aprint


@lru_cache
def get_function_signature(function_name: str, include_docstring: bool = False) -> str:
    """Retrieve the signature of a function given its fully qualified name.

    Imports the function and builds a ``def`` signature string with
    parameter types, defaults, and return type. Optionally includes
    parsed docstring sections (Description, Parameters, Returns).

    Args:
        function_name: Fully qualified dotted name (e.g., "numpy.array").
        include_docstring: If True, append parsed docstring sections.

    Returns:
        The function signature as a string, or None if the function
        cannot be found or imported.
    """
    try:
        module_name, function_name = function_name.rsplit(".", 1)
        module = __import__(module_name, fromlist=[function_name])
        function = getattr(module, function_name)
        signature = inspect.signature(function)

        # Get function parameters
        parameters = []
        for name, param in signature.parameters.items():
            if param.annotation != inspect.Parameter.empty:
                if param.default != inspect.Parameter.empty:
                    default_value = str(param.default)
                    parameters.append(
                        f"{name}: {param.annotation.__name__} = {default_value}"
                    )
                else:
                    parameters.append(f"{name}: {param.annotation.__name__}")
            else:
                parameters.append(name)

        # get the return type:
        if signature.return_annotation != inspect.Signature.empty:
            return_type = f" -> {str(signature.return_annotation.__name__)}"
        else:
            return_type = f""

        # Get function name and signature
        function_signature = (
            f"def {function_name}({', '.join(parameters)}){return_type}:"
        )

        # Include docstring if flag is True
        if include_docstring:
            docstring = inspect.getdoc(function)
            if docstring:
                lines = docstring.strip().split("\n")
                sections = {"Description": ""}
                current_section = "Description"
                for i, line in enumerate(lines):
                    try:
                        line_stripped = line.strip()
                        if line_stripped.startswith("----"):
                            current_section = lines[i - 1].strip()
                            sections[current_section] = ""
                        else:
                            if (
                                current_section
                                and i + 1 < len(lines)
                                and not lines[i + 1].startswith("----")
                            ):
                                sections[current_section] += line + "\n"
                    except Exception:
                        traceback.print_exc()
                        aprint(f"Issue while parsing docstring line {i}: {line} ")

                desc_section = sections.get("Description", "")
                param_section = sections.get("Parameters", "")
                return_section = sections.get("Returns", "")

                if desc_section:
                    function_signature += f"\n\nDescription\n---------\n{desc_section}"
                if param_section:
                    function_signature += f"\n\nParameters\n---------\n{param_section}"
                if return_section:
                    function_signature += f"\n\nReturns\n------\n{return_section}"

        return function_signature

    except (ImportError, AttributeError, ValueError, TypeError):
        return None


@lru_cache
def object_info_str(
    obj: Any, add_docstrings: bool = True, show_hidden: bool = False
) -> str:
    """Return a string listing all public methods and their signatures for an object.

    Args:
        obj: The Python object to inspect.
        add_docstrings: If True, include method docstrings.
        show_hidden: If True, include methods starting with underscore.

    Returns:
        A formatted string with the class name and all method signatures.
    """
    methods = enumerate_methods(
        obj, add_docstrings=add_docstrings, show_hidden=show_hidden
    )

    methods = list(methods)

    info = f"Class {type(obj)}: "
    info += "\n".join(methods)

    return info


@lru_cache
def enumerate_methods(
    obj: Any, add_docstrings: bool = True, show_hidden: bool = False
) -> list[str]:
    """Yield signature strings for each callable method of an object.

    Args:
        obj: The Python object to inspect.
        add_docstrings: If True, append each method's docstring.
        show_hidden: If True, include methods starting with underscore.

    Yields:
        Formatted strings containing method signatures and optional docstrings.
    """
    # List to hold methods:
    methods = []

    # Get the list of methods of the object
    for method_name in dir(obj):
        try:
            if not show_hidden and method_name.startswith("_"):
                continue

            method = getattr(obj, method_name)
            if callable(method):
                methods.append(method_name)
        except Exception:
            continue

    # Print the signature for each method with type hints
    for method_name in methods:
        method_info = ""
        try:
            method = getattr(obj, method_name)
            method_info += get_signature(method)
            if add_docstrings:
                method_info += "\n"
                method_info += method.__doc__
                method_info += "\n"

            yield method_info

        except Exception:
            # Something happened, we skip!
            continue


@lru_cache
def get_signature(method):
    """Build a human-readable signature string for a callable.

    Args:
        method: A callable whose signature to format.

    Returns:
        A string like ``"func_name(arg1: int, arg2: str = 'default')"``.
    """
    method_name = getattr(method, "__name__", repr(method))
    argspec = inspect.getfullargspec(method)
    arg_names = argspec.args
    arg_defaults = argspec.defaults or ()
    num_defaults = len(arg_defaults)
    arg_types = get_type_hints(method)
    signature_parts = []
    for i, arg_name in enumerate(arg_names):
        arg_type = arg_types.get(arg_name, None)
        if i >= len(arg_names) - num_defaults:
            default_value = arg_defaults[i - len(arg_names) + num_defaults]
            default_str = repr(default_value)
            signature_parts.append(
                f"{arg_name}{': ' + arg_type.__name__ if arg_type else ''} = {default_str}"
            )
        else:
            signature_parts.append(
                f"{arg_name}{': ' + arg_type.__name__ if arg_type else ''}"
            )
    signature = f"{method_name}({', '.join(signature_parts)})"
    return signature


@lru_cache
def get_function_info(function_path: str, add_docstrings: bool = False):
    """Get signature and optional docstring for a function by its dotted path.

    First attempts a direct import. If that fails, progressively searches
    broader parent packages for the function name.

    Args:
        function_path: Fully qualified dotted path (e.g., "scipy.ndimage.convolve").
        add_docstrings: If True, include the function's docstring.

    Returns:
        A string with the function signature (and docstring), or a
        "not found" message.
    """
    parts = function_path.split(".")
    function_name = parts[-1]

    # Try direct import first (fast path):
    sig = get_function_signature(function_path, include_docstring=add_docstrings)
    if sig:
        # Replace "def func(" with "def module.func(" for
        # consistency with the recursive search path:
        module_name = ".".join(parts[:-1])
        if module_name and sig.startswith(f"def {function_name}("):
            sig = sig.replace(
                f"def {function_name}(",
                f"def {function_path}(",
                1,
            )
        return sig

    # Fallback: search progressively broader packages.
    # e.g. for "skimage.morphology.watershed", try
    # "skimage.morphology" first, then "skimage":
    for depth in range(len(parts) - 1, 0, -1):
        pkg_name = ".".join(parts[:depth])
        info = find_function_info_in_package(
            pkg_name=pkg_name,
            function_name=function_name,
            add_docstrings=add_docstrings,
        )
        if len(info) > 0:
            return "\n\n".join(info)

    return f"Function {function_path} not found."


def find_functions_in_package(pkg_name: str, function_name: str):
    """Recursively search a package for functions matching a given name.

    Args:
        pkg_name: Dotted package name to search (e.g., "scipy.ndimage").
        function_name: The function name to look for.

    Returns:
        A list of (package_path, function_object) tuples for each match.
    """
    import warnings  # to ignore deprecation warnings

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        try:
            pkg = importlib.import_module(pkg_name)
        except ModuleNotFoundError:
            return []

        functions = []
        for name, obj in inspect.getmembers(pkg):
            if name.startswith("_"):
                continue
            if inspect.ismodule(obj):
                recursive_functions = find_functions_in_package(
                    pkg_name + "." + name, function_name
                )
                if recursive_functions:
                    functions += recursive_functions
            elif inspect.isfunction(obj) and obj.__name__ == function_name:
                functions.append((pkg_name, obj))

        return functions


def find_function_info_in_package(
    pkg_name: str, function_name: str, add_docstrings: bool = True
):
    """Search a package for functions by name and return their signatures.

    Args:
        pkg_name: Dotted package name to search.
        function_name: The function name to look for.
        add_docstrings: If True, include each function's docstring.

    Returns:
        A list of formatted signature strings (with optional docstrings).
    """
    functions = find_functions_in_package(pkg_name, function_name)

    info_list = []
    for p, f in functions:
        try:
            signature = p + "." + get_signature(f)
            function_info = signature
            if add_docstrings:
                function_info += "\n"
                function_info += f.__doc__
                function_info += "\n"

            info_list.append(function_info)
        except TypeError:
            # The method is a built-in function or method, which is not supported by getfullargspec
            continue

    return info_list


@lru_cache
def extract_package_path(path: str):
    """Extract a dotted package/function path from a natural-language string.

    Prefers the longest dotted qualified name found (e.g., "scipy.ndimage.convolve").
    Falls back to the last standalone word if no dotted name is found.

    Args:
        path: A string that may contain a dotted package path.

    Returns:
        The extracted package path string, or None if no match is found.
    """
    # Match dotted qualified names (e.g. scipy.ndimage.convolve)
    # requiring at least one dot to distinguish from plain words:
    dotted_pattern = re.compile(r"\b\w+(?:\.\w+)+\b")
    matches = dotted_pattern.findall(path)
    if matches:
        # Return the longest match (most specific):
        return max(matches, key=len)

    # Fallback: single word (e.g. just "numpy").
    # Use the last word since query terms typically appear
    # at the end of natural language requests:
    word_pattern = re.compile(r"\b\w+\b")
    matches = word_pattern.findall(path)
    if matches:
        return matches[-1]

    return None


@lru_cache
def extract_fully_qualified_function_names(
    code: str, unzip_result: bool = False
) -> list[str]:
    """Extract fully qualified function names from Python source code via AST.

    Parses import statements and function calls to resolve short names
    to their fully qualified forms (e.g., ``np.array`` -> ``numpy.array``).

    Args:
        code: Python source code to parse.
        unzip_result: If True, return two parallel lists (qualified names,
            original call expressions) instead of a list of tuples.

    Returns:
        A list of (fully_qualified_name, original_call) tuples, or two
        parallel lists if unzip_result is True. Returns None on parse error.
    """
    try:
        function_calls = []
        import_statements = {}

        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    import_statements[alias.asname or module_name] = module_name

            elif isinstance(node, ast.ImportFrom):
                module_name = node.module
                for item in node.names:
                    import_statements[item.asname or item.name] = (
                        module_name + "." + item.name
                    )

            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                module_name = ""
                if isinstance(node.func.value, ast.Name):
                    module_name = node.func.value.id
                elif isinstance(node.func.value, ast.Attribute):
                    module_name = node.func.value.value.id + "." + node.func.value.attr

                function_name = node.func.attr
                if module_name and function_name:
                    if module_name in import_statements:
                        fully_qualified_module_name = import_statements[module_name]
                        fully_qualified_function_name = (
                            fully_qualified_module_name + "." + function_name
                        )
                        original_function_call = module_name + "." + function_name
                        function_calls.append(
                            (fully_qualified_function_name, original_function_call)
                        )

        if unzip_result:
            function_calls = unzip(function_calls)

        return function_calls
    except Exception:
        traceback.print_exc()
        return None


def unzip(list_of_tuples):
    """Transpose a list of tuples into a list of lists.

    Args:
        list_of_tuples: A list of tuples to unzip.

    Returns:
        A list of lists, one per tuple position.
    """
    unzipped = zip(*list_of_tuples)
    return [list(items) for items in unzipped]


@lru_cache
def function_exists(function_name: str) -> bool:
    """Check whether a fully qualified function name can be imported and called.

    Args:
        function_name: Fully qualified dotted name (e.g., "os.path.exists").

    Returns:
        True if the function exists and is callable.
    """
    try:
        module_name, function_name = function_name.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return hasattr(module, function_name) and callable(
            getattr(module, function_name)
        )
    except (ValueError, ImportError, AttributeError):
        return False


@lru_cache
def get_imported_modules(code: str) -> list[str]:
    """Extract module names from all import statements in Python source code.

    Args:
        code: Python source code to parse.

    Returns:
        A list of unique module name strings found in import statements.
    """
    tree = ast.parse(code)
    imported_modules = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.add(node.module)

    return list(imported_modules)


# def find_functions_with_name(module_list: List[str], function_name: str) -> List[str]:
#     functions = []
#
#     for module_name in module_list:
#         for importer, package_name, _ in pkgutil.iter_modules():
#             if package_name.startswith(module_name):
#                 package_path = importer.path
#
#                 for root, _, files in os.walk(package_path):
#                     for file_name in files:
#                         try:
#                             if file_name.endswith(".py"):
#                                 file_path = os.path.join(root, file_name)
#                                 module = parse_module(file_path)
#                                 found_functions = find_functions_in_module(module,
#                                                                            function_name)
#                                 functions.extend(found_functions)
#                         except Exception as e:
#                             aprint(f'Error while reading or parsing {file_name}: {str(e)}')
#
#     return functions
#
# @lru_cache
# def parse_module(file_path):
#     with open(file_path, "r") as file:
#         code = file.read()
#
#     return ast.parse(code, file_path)
#
#
# @lru_cache
# def find_functions_in_module(module, function_name):
#     functions = []
#
#     for node in ast.walk(module):
#         if isinstance(node, ast.FunctionDef) and node.name == function_name:
#             module_name = inspect.getmodulename(module.filename)
#             functions.append(f"{module_name}.{node.name}")
#
#     return functions
