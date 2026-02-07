"""Test for Fix 11: importing exception_catcher_tool module."""

import importlib
import sys


def test_import_does_not_modify_excepthook():
    """Import should not change excepthook; only __init__ should."""
    original_hook = sys.excepthook

    # Force re-import of the module
    mod_name = "napari_chatgpt.omega_agent.tools" ".special.exception_catcher_tool"
    if mod_name in sys.modules:
        del sys.modules[mod_name]

    importlib.import_module(mod_name)

    # Import alone should NOT change excepthook
    assert sys.excepthook is original_hook

    # Instantiate the tool — this should install the hook
    from napari_chatgpt.omega_agent.tools.special import (
        exception_catcher_tool as ect,
    )

    ExceptionCatcherTool = ect.ExceptionCatcherTool

    tool = ExceptionCatcherTool()
    assert sys.excepthook is not original_hook
    assert tool._original_excepthook is original_hook

    # Restore
    sys.excepthook = original_hook
