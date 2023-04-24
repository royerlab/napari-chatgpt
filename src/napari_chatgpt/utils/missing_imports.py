import ast
import pkgutil


def get_missing_imports(code):
    tree = ast.parse(code)
    missing_imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name
                if not _module_available(module_name):
                    missing_imports.add(module_name)
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module
            if not _module_available(module_name):
                missing_imports.add(module_name)

    required_imports = _get_required_imports(code)
    available_modules = set(pkgutil.iter_modules())

    for module_name in required_imports:
        if not _module_available(module_name):
            for module in available_modules:
                if module.name == module_name:
                    missing_imports.add(f"import {module_name}")

    return missing_imports


def _get_required_imports(code):
    tree = ast.parse(code)
    required_imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                required_imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module
            if module_name is not None:
                required_imports.add(module_name)

    return required_imports


def _module_available(module_name):
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False
