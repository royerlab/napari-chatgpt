import ast
import importlib
import inspect
import re
import traceback
from functools import lru_cache
from typing import get_type_hints, Any, List

from arbol import aprint


@lru_cache
def get_function_signature(function_name: str, include_docstring: bool = False) -> str:
    """
    Return the signature of a fully qualified Python function as a string, optionally including its parsed docstring.
    
    Parameters:
        function_name (str): Fully qualified function name (e.g., "module.submodule.function").
        include_docstring (bool): If True, appends parsed docstring sections ("Description", "Parameters", "Returns") to the signature.
    
    Returns:
        str: The function signature string, or None if the function cannot be found.
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

    except (ImportError, AttributeError):
        return None


@lru_cache
def object_info_str(
    obj: Any, add_docstrings: bool = True, show_hidden: bool = False
) -> str:
    """
    Return a string describing the object's class and its methods, optionally including docstrings and hidden methods.
    
    Parameters:
        obj (Any): The object to introspect.
        add_docstrings (bool): If True, includes method docstrings in the output.
        show_hidden (bool): If True, includes methods whose names start with an underscore.
    
    Returns:
        str: A formatted string listing the object's class and its methods.
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
) -> List[str]:
    # List to hold methods:
    """
    Yields formatted signatures and optional docstrings for all callable methods of an object.
    
    Parameters:
        add_docstrings (bool): If True, includes each method's docstring in the output.
        show_hidden (bool): If True, includes methods whose names start with an underscore.
    
    Yields:
        str: A string containing the method's signature and, if requested, its docstring.
    """
    methods = []

    # Get the list of methods of the object
    for method_name in dir(obj):
        try:
            if not show_hidden and method_name.startswith("_"):
                continue

            method = getattr(obj, method_name)
            if callable(method):
                methods.append(method_name)
        except:
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
    """
    Return a string representation of a method's signature, including argument names, types (if annotated), and default values.
    
    Parameters:
        method: The function or method object to introspect.
    
    Returns:
        str: The formatted signature string, e.g., "func(arg1: int, arg2 = 5)".
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
    """
    Retrieve information about a function given its fully qualified path.
    
    Parameters:
        function_path (str): The fully qualified path to the function (e.g., "package.module.function").
        add_docstrings (bool): If True, includes the function's docstring in the output.
    
    Returns:
        str: A formatted string with the function's signature and optionally its docstring, or a not found message if the function does not exist.
    """
    splitted_function_path = function_path.split(".")

    function_name = splitted_function_path[-1]
    pkg_name = ".".join(splitted_function_path[0:-2])

    info = find_function_info_in_package(
        pkg_name=pkg_name, function_name=function_name, add_docstrings=add_docstrings
    )

    if len(info) > 0:
        return "\n\n".join(info)
    else:
        return f"Function {function_path} not found."


def find_functions_in_package(pkg_name: str, function_name: str):
    """
    Recursively search a package and its submodules for functions matching a given name.
    
    Parameters:
        pkg_name (str): The fully qualified name of the package to search.
        function_name (str): The name of the function to find.
    
    Returns:
        List[Tuple[str, function]]: A list of tuples containing the module name and function object for each match found.
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
    """
    Finds all functions with a given name in a package and returns their fully qualified signatures, optionally including docstrings.
    
    Parameters:
        pkg_name (str): The name of the package to search within.
        function_name (str): The name of the function to locate.
        add_docstrings (bool): If True, includes the function's docstring in the output.
    
    Returns:
        List[str]: A list of strings, each containing the fully qualified function signature and, if requested, its docstring.
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
    """
    Extracts the package name from a string using a regular expression.
    
    Parameters:
        path (str): The string from which to extract the package name.
    
    Returns:
        str or None: The extracted package name if found, otherwise None.
    """
    package_name_pattern = re.compile(r"\b\w+(\.\w+)*\b")

    match = package_name_pattern.search(path)
    if match:
        package_name = match.group()
        return package_name
    else:
        return None


@lru_cache
def extract_fully_qualified_function_names(
    code: str, unzip_result: bool = False
) -> List[str]:
    """
    Extracts fully qualified function names from Python source code by analyzing import statements and function calls.
    
    Parses the provided code to identify function calls on imported modules or objects, resolving their fully qualified names using the import map. Returns a list of tuples containing the fully qualified function name and the original function call. If `unzip_result` is True, returns separate lists of fully qualified names and original calls. Returns None if parsing fails.
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
    except:
        traceback.print_exc()
        return None


def unzip(list_of_tuples):
    """
    Unzip a list of tuples into separate lists, grouping elements by their position.
    
    Parameters:
        list_of_tuples (list of tuple): The list of tuples to unzip.
    
    Returns:
        list of list: A list containing separate lists for each position in the tuples.
    """
    unzipped = zip(*list_of_tuples)
    return [list(items) for items in unzipped]


@lru_cache
def function_exists(function_name: str) -> bool:
    """
    Check if a fully qualified function name refers to an existing callable function.
    
    Parameters:
        function_name (str): The fully qualified name of the function (e.g., "module.submodule.function").
    
    Returns:
        bool: True if the function exists and is callable, False otherwise.
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
def get_imported_modules(code: str) -> List[str]:
    """
    Extracts all module names imported in the given Python source code.
    
    Parameters:
        code (str): Python source code as a string.
    
    Returns:
        List[str]: A list of unique module names imported via `import` or `from ... import` statements.
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
