import re
from typing import get_type_hints, Any, List


def object_info_str(obj: Any,
                    add_docstrings: bool = True,
                    show_hidden: bool = False) -> str:
    methods = enumerate_methods(obj,
                                add_docstrings=add_docstrings,
                                show_hidden=show_hidden)

    methods = list(methods)

    info = f'Class {type(obj)}: '
    info += '\n'.join(methods)

    return info


def enumerate_methods(obj: Any,
                      add_docstrings: bool = True,
                      show_hidden: bool = False) -> List[str]:
    # List to hold methods:
    methods = []

    # Get the list of methods of the object
    for method_name in dir(obj):
        try:
            if not show_hidden and method_name.startswith('_'):
                continue

            method = getattr(obj, method_name)
            if callable(method):
                methods.append(method_name)
        except:
            continue

    # Print the signature for each method with type hints
    for method_name in methods:
        method_info = ''
        try:
            method = getattr(obj, method_name)
            method_info += get_signature(method)
            if add_docstrings:
                method_info += '\n'
                method_info += method.__doc__
                method_info += '\n'

            yield method_info

        except Exception:
            # Something happened, we skip!
            continue


def get_signature(method):
    method_name = getattr(method, '__name__', repr(method))
    argspec = inspect.getfullargspec(method)
    arg_names = argspec.args
    arg_defaults = argspec.defaults or ()
    num_defaults = len(arg_defaults)
    arg_types = get_type_hints(method)
    signature_parts = []
    for i, arg_name in enumerate(arg_names):
        arg_type = arg_types.get(arg_name, None)
        if i >= len(arg_names) - num_defaults:
            default_value = arg_defaults[
                i - len(arg_names) + num_defaults]
            default_str = repr(default_value)
            signature_parts.append(
                f"{arg_name}{': ' + arg_type.__name__ if arg_type else ''} = {default_str}")
        else:
            signature_parts.append(
                f"{arg_name}{': ' + arg_type.__name__ if arg_type else ''}")
    signature = f"{method_name}({', '.join(signature_parts)})"
    return signature


import importlib
import inspect


def get_function_info(function_path: str,
                      add_docstrings: bool = False):
    splitted_function_path = function_path.split('.')

    function_name = splitted_function_path[-1]
    pkg_name = '.'.join(splitted_function_path[0:-2])

    info = find_function_info_in_package(pkg_name=pkg_name,
                                         function_name=function_name,
                                         add_docstrings=add_docstrings)

    if len(info) > 0:
        return '\n\n'.join(info)
    else:
        return f'Function {function_path} not found.'


def find_functions_in_package(pkg_name: str, function_name: str):
    try:
        pkg = importlib.import_module(pkg_name)
    except ModuleNotFoundError:
        return []

    functions = []
    for name, obj in inspect.getmembers(pkg):
        if name.startswith('_'):
            continue
        if inspect.ismodule(obj):
            recursive_functions = find_functions_in_package(
                pkg_name + '.' + name, function_name)
            if recursive_functions:
                functions += recursive_functions
        elif inspect.isfunction(obj) and obj.__name__ == function_name:
            functions.append((pkg_name, obj))

    return functions


def find_function_info_in_package(pkg_name: str,
                                  function_name: str,
                                  add_docstrings: bool = True):
    functions = find_functions_in_package(pkg_name, function_name)

    info_list = []
    for p, f in functions:
        try:
            signature = p + '.' + get_signature(f)
            function_info = signature
            if add_docstrings:
                function_info += '\n'
                function_info += f.__doc__
                function_info += '\n'

            info_list.append(function_info)
        except TypeError:
            # The method is a built-in function or method, which is not supported by getfullargspec
            continue

    return info_list


def extract_package_path(path: str):
    package_name_pattern = re.compile(r'\b\w+(\.\w+)*\b')

    match = package_name_pattern.search(path)
    if match:
        package_name = match.group()
        return package_name
    else:
        return None
