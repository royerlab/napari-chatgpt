"""Test for Fix 11: importing exception_catcher_tool module."""

import importlib
import sys

_ECT = "napari_chatgpt.omega_agent.tools" ".special.exception_catcher_tool"


def _import_ect():
    """Import the exception_catcher_tool module."""
    import napari_chatgpt.omega_agent.tools.special.exception_catcher_tool as m

    return m


def test_import_does_not_modify_excepthook():
    """Import should not change excepthook; only __init__ should."""
    original_hook = sys.excepthook

    # Force re-import of the module
    if _ECT in sys.modules:
        del sys.modules[_ECT]

    importlib.import_module(_ECT)

    # Import alone should NOT change excepthook
    assert sys.excepthook is original_hook

    # Instantiate the tool — this should install the hook
    ect = _import_ect()

    tool = ect.ExceptionCatcherTool()
    assert sys.excepthook is not original_hook
    assert tool._original_excepthook is original_hook

    # Restore
    sys.excepthook = original_hook


def test_run_omega_tool_empty_queue():
    """Verify empty queue returns 'No exceptions'."""
    original_hook = sys.excepthook

    ect = _import_ect()

    # Drain the queue first:
    while not ect.exception_queue.empty():
        ect.exception_queue.get_nowait()

    tool = ect.ExceptionCatcherTool()
    result = tool.run_omega_tool("1")
    assert "No exceptions recorded" in result

    sys.excepthook = original_hook


def test_run_omega_tool_with_exception():
    """Verify queued exception is reported."""
    original_hook = sys.excepthook

    ect = _import_ect()

    # Drain the queue first:
    while not ect.exception_queue.empty():
        ect.exception_queue.get_nowait()

    tool = ect.ExceptionCatcherTool()

    # Create and enqueue an exception with traceback:
    try:
        raise RuntimeError("test error for catcher")
    except RuntimeError as e:
        ect.enqueue_exception(e)

    result = tool.run_omega_tool("1")
    assert "test error for catcher" in result
    assert "RuntimeError" in result

    sys.excepthook = original_hook
