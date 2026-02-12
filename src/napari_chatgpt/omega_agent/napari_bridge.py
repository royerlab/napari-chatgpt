"""Thread-safe bridge between the Omega agent and the napari Qt event loop.

This module provides ``NapariBridge``, which uses a pair of queues and
napari's ``@thread_worker`` decorator to safely execute arbitrary callables
on the Qt thread from a background (non-GUI) thread. It also maintains a
thread-safe global cache of viewer information so that tools can inspect
viewer state without blocking the Qt thread.
"""

import threading
from collections.abc import Callable
from queue import Empty, Queue

import napari
import napari.viewer
from arbol import aprint, asection
from napari import Viewer
from napari.qt.threading import thread_worker
from PIL.Image import fromarray

from napari_chatgpt.omega_agent.tools.special.exception_catcher_tool import (
    enqueue_exception,
)
from napari_chatgpt.utils.napari.napari_viewer_info import get_viewer_info
from napari_chatgpt.utils.python.exception_guard import ExceptionGuard

# Thread-safe global variable to exchange information with the viewer:
_viewer_info_lock = threading.Lock()
_viewer_info = None


def _set_viewer_info(viewer_info):
    """Store viewer information in the thread-safe global cache.

    Args:
        viewer_info: Serialised viewer state to cache.
    """
    global _viewer_info
    with _viewer_info_lock:
        _viewer_info = viewer_info


def _get_viewer_info():
    """Retrieve the cached viewer information in a thread-safe manner.

    Returns:
        The most recently cached viewer information, or ``None``.
    """
    with _viewer_info_lock:
        return _viewer_info


class NapariBridge:
    """Queue-based bridge for executing code on napari's Qt thread.

    The bridge spawns a background ``@thread_worker`` that polls a
    *to_napari_queue* for callables. Each callable is yielded so that
    napari's signal/slot mechanism invokes it on the Qt event loop. The
    result (or any caught exception) is placed on a *from_napari_queue*
    for the caller to retrieve.

    Attributes:
        viewer: The napari ``Viewer`` instance this bridge is bound to.
        to_napari_queue: Queue for sending callables to the Qt thread.
        from_napari_queue: Queue for receiving results from the Qt thread.
    """

    def __init__(self, viewer: Viewer):
        self.viewer = viewer

        self.to_napari_queue = Queue(maxsize=16)
        self.from_napari_queue = Queue(maxsize=16)

        #
        def qt_code_executor(fun: Callable[[napari.Viewer], None]):
            with asection(f"qt_code_executor received delegated function."):
                with ExceptionGuard() as guard:
                    aprint("Executing now!")
                    result = fun(viewer)
                    aprint(result)
                    self.from_napari_queue.put(result)

                if guard.exception:
                    aprint(
                        f"Exception while executing on napari's QT thread:\n{guard.exception_description}"
                    )
                    self.from_napari_queue.put(guard)
                    enqueue_exception(guard.exception_value)

        self._stop_flag = False

        @thread_worker(connect={"yielded": qt_code_executor})
        def omega_napari_worker(to_napari_queue: Queue, from_napari_queue: Queue):
            while not self._stop_flag:

                # get code from the queue (with timeout so we can check the stop flag):
                try:
                    code = to_napari_queue.get(timeout=1.0)
                except Empty:
                    continue

                # execute code on napari's QT thread:
                if code is None:
                    break  # stops.

                yield code

        # create the worker:
        self.worker = omega_napari_worker(self.to_napari_queue, self.from_napari_queue)

    def get_viewer_info(self) -> str:
        """Collect viewer state information on the Qt thread and return it.

        Returns:
            A string summarising the current viewer state, or an error
            message if the information could not be retrieved.
        """

        # Setting up delegated function:
        delegated_function = lambda v: get_viewer_info(v)

        try:
            # execute delegated function in napari context:
            info = self._execute_in_napari_context(delegated_function)

            return info

        except Exception as e:
            # print exception stack trace:
            import traceback

            traceback.print_exc()

            return "Could not get information about the viewer because of an error."

    def take_snapshot(self):
        """Take a screenshot of the napari viewer on the Qt thread.

        Returns:
            A ``PIL.Image.Image`` of the full napari window, or ``None``
            / an error string if the screenshot fails.
        """

        # Delegated function:
        def _delegated_snapshot_function(viewer: Viewer):
            # Take a screenshot of the whole Napari viewer
            screenshot = self.viewer.screenshot(canvas_only=False, flash=False)

            # Convert the screenshot (NumPy array) to a PIL image
            pil_image = fromarray(screenshot)

            return pil_image

        # Execute delegated function in napari context and return result:
        return self._execute_in_napari_context(_delegated_snapshot_function)

    def stop(self):
        """Signal the background worker to exit."""
        self._stop_flag = True
        try:
            self.to_napari_queue.put_nowait(None)
        except Exception:
            pass

    def _execute_in_napari_context(self, delegated_function, timeout: float = 300.0):
        """Execute a callable in napari's Qt context via the queue bridge.

        The callable is placed on ``to_napari_queue`` and the method blocks
        until a result appears on ``from_napari_queue`` or the timeout
        elapses.

        Args:
            delegated_function: A callable accepting a ``napari.Viewer``
                and returning an arbitrary result.
            timeout: Maximum seconds to wait for a response. Defaults to
                300 (5 minutes).

        Returns:
            The value returned by *delegated_function*, an error message
            string if an exception was caught, or ``None`` on unexpected
            failure.
        """
        try:
            # Send code to napari:
            self.to_napari_queue.put(delegated_function)

            # Get response with timeout to prevent deadlocks:
            try:
                response = self.from_napari_queue.get(timeout=timeout)
            except Empty:
                aprint(f"Timeout waiting for napari response after {timeout}s")
                return f"Error: Timeout waiting for napari to respond after {timeout} seconds."

            if isinstance(response, ExceptionGuard):
                exception_guard = response
                # print stack trace:
                import traceback

                traceback.print_exc()
                # raise exception_guard.exception
                return f"Error: {exception_guard.exception_type_name} with message: '{str(exception_guard.exception)}' ."

            return response

        except Exception:
            # print exception stack trace:
            import traceback

            traceback.print_exc()

            return None
