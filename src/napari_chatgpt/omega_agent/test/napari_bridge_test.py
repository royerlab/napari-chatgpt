"""Tests for NapariBridge functionality using mocked queues."""

from queue import Empty, Queue
from unittest.mock import MagicMock, patch

from napari_chatgpt.omega_agent.napari_bridge import (
    NapariBridge,
    _get_viewer_info,
    _set_viewer_info,
)
from napari_chatgpt.utils.python.exception_guard import ExceptionGuard


class TestExecuteInNapariContext:
    """Test _execute_in_napari_context by constructing a bridge with mocked internals."""

    def _make_bridge_with_mocked_queues(self):
        """Create a NapariBridge-like object with mocked queues, bypassing __init__."""
        bridge = object.__new__(NapariBridge)
        bridge.to_napari_queue = Queue()
        bridge.from_napari_queue = Queue()
        bridge.viewer = MagicMock()
        return bridge

    def test_happy_path(self):
        bridge = self._make_bridge_with_mocked_queues()
        bridge.from_napari_queue.put("result_value")

        result = bridge._execute_in_napari_context(lambda v: "ignored", timeout=1.0)

        assert result == "result_value"

    def test_timeout_path(self):
        bridge = self._make_bridge_with_mocked_queues()
        # from_napari_queue is empty, so get() will timeout

        result = bridge._execute_in_napari_context(lambda v: "ignored", timeout=0.1)

        assert "Timeout" in result

    def test_exception_guard_response(self):
        bridge = self._make_bridge_with_mocked_queues()
        guard = ExceptionGuard(print_stacktrace=False)
        guard.exception = ValueError
        guard.exception_type_name = "ValueError"
        guard.exception_value = ValueError("test error")
        bridge.from_napari_queue.put(guard)

        result = bridge._execute_in_napari_context(lambda v: "ignored", timeout=1.0)

        assert "Error" in result
        assert "ValueError" in result

    def test_put_exception_path(self):
        bridge = self._make_bridge_with_mocked_queues()
        # Make to_napari_queue.put() raise an exception
        bridge.to_napari_queue = MagicMock()
        bridge.to_napari_queue.put.side_effect = RuntimeError("queue broken")

        result = bridge._execute_in_napari_context(lambda v: "ignored", timeout=1.0)

        assert result is None


class TestViewerInfoThreadSafety:
    """Test _set_viewer_info and _get_viewer_info global functions."""

    def test_set_and_get(self):
        _set_viewer_info("test info")
        assert _get_viewer_info() == "test info"

    def test_set_none(self):
        _set_viewer_info(None)
        assert _get_viewer_info() is None

    def test_overwrite(self):
        _set_viewer_info("first")
        _set_viewer_info("second")
        assert _get_viewer_info() == "second"
