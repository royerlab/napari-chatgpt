"""Tests for security fixes in pip_utils.py and conda_utils.py.

These tests verify that subprocess calls use list-based arguments
instead of shell=True to prevent shell injection vulnerabilities.
"""

import ast
import inspect

import pytest


def test_pip_uninstall_does_not_use_shell_true():
    """Test that pip_uninstall does not use shell=True.

    This test verifies the fix for the shell injection vulnerability
    where subprocess.run was called with shell=True.
    """
    from napari_chatgpt.utils.python import pip_utils

    source = inspect.getsource(pip_utils.pip_uninstall)

    # Parse the source code
    tree = ast.parse(source)

    # Find all subprocess.run calls
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check if this is a subprocess.run call
            if isinstance(node.func, ast.Attribute) and node.func.attr == "run":
                # Check keyword arguments for shell=True
                for keyword in node.keywords:
                    if keyword.arg == "shell":
                        # shell should not be True
                        if isinstance(keyword.value, ast.Constant):
                            assert (
                                keyword.value.value is not True
                            ), "pip_uninstall should not use shell=True"


def test_conda_install_does_not_use_shell_true():
    """Test that conda_install does not use shell=True.

    This test verifies the fix for the shell injection vulnerability.
    """
    from napari_chatgpt.utils.python import conda_utils

    source = inspect.getsource(conda_utils.conda_install)

    # Check that 'shell=True' is not in the source
    assert "shell=True" not in source, "conda_install should not use shell=True"


def test_conda_uninstall_does_not_use_shell_true():
    """Test that conda_uninstall does not use shell=True.

    This test verifies the fix for the shell injection vulnerability.
    """
    from napari_chatgpt.utils.python import conda_utils

    source = inspect.getsource(conda_utils.conda_uninstall)

    # Check that 'shell=True' is not in the source
    assert "shell=True" not in source, "conda_uninstall should not use shell=True"


def test_conda_install_uses_list_args():
    """Test that conda_install uses list-based arguments for subprocess."""
    from napari_chatgpt.utils.python import conda_utils

    source = inspect.getsource(conda_utils.conda_install)

    # Should contain list construction for command
    assert (
        '["conda"' in source or "['conda'" in source
    ), "conda_install should use list-based command arguments"


def test_conda_uninstall_uses_list_args():
    """Test that conda_uninstall uses list-based arguments for subprocess."""
    from napari_chatgpt.utils.python import conda_utils

    source = inspect.getsource(conda_utils.conda_uninstall)

    # Should contain list construction for command
    assert (
        '["conda"' in source or "['conda'" in source
    ), "conda_uninstall should use list-based command arguments"


def test_pip_uninstall_uses_sys_executable():
    """Test that pip_uninstall uses sys.executable for Python path."""
    from napari_chatgpt.utils.python import pip_utils

    source = inspect.getsource(pip_utils.pip_uninstall)

    # Should use sys.executable for reliable pip invocation
    assert "sys.executable" in source, "pip_uninstall should use sys.executable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
