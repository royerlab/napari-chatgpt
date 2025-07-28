from queue import Queue
from typing import Callable

import napari
import napari.viewer
from PIL.Image import fromarray
from arbol import aprint, asection
from napari import Viewer
from napari.qt.threading import thread_worker

from napari_chatgpt.omega_agent.tools.special.exception_catcher_tool import (
    enqueue_exception,
)
from napari_chatgpt.utils.napari.napari_viewer_info import get_viewer_info
from napari_chatgpt.utils.python.exception_guard import ExceptionGuard

# global Variable to exchange information with the viewer:
_viewer_info = None


def _set_viewer_info(viewer_info):
    """
    Set the global viewer information used by the bridge.
    
    Parameters:
    	viewer_info: The viewer information object to store globally.
    """
    global _viewer_info
    _viewer_info = viewer_info


def _get_viewer_info():
    """
    Retrieve the current viewer information stored in the global variable.
    
    Returns:
        The value of the global `_viewer_info`, which contains viewer-related information.
    """
    global _viewer_info
    return _viewer_info


class NapariBridge:

    def __init__(self, viewer: Viewer):
        """
        Initialize the NapariBridge with a Napari Viewer instance and set up inter-thread communication for executing functions on the Napari Qt thread.
        
        Creates internal queues for delegating functions to the Qt thread and receiving results, and starts a worker to process these function calls.
        """
        self.viewer = viewer

        self.to_napari_queue = Queue(maxsize=16)
        self.from_napari_queue = Queue(maxsize=16)

        #
        def qt_code_executor(fun: Callable[[napari.Viewer], None]):
            """
            Executes a delegated function on the Napari Qt thread and communicates the result or any exception via a queue.
            
            If an exception occurs during execution, it is captured and both the exception and its details are sent through the queue for external handling.
            """
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

        @thread_worker(connect={"yielded": qt_code_executor})
        def omega_napari_worker(to_napari_queue: Queue, from_napari_queue: Queue):
            """
            Continuously retrieves functions from a queue and yields them for execution on Napari's Qt thread.
            
            The worker runs until it receives a `None` value, which signals it to stop.
            """
            while True:

                # get code from the queue:
                code = to_napari_queue.get()

                # execute code on napari's QT thread:
                if code is None:
                    break  # stops.

                yield code

        # create the worker:
        self.worker = omega_napari_worker(self.to_napari_queue, self.from_napari_queue)

    def get_viewer_info(self) -> str:

        # Setting up delegated function:
        """
        Retrieve information about the current Napari viewer.
        
        Returns:
            str: A string containing viewer information, or an error message if retrieval fails.
        """
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

        # Delegated function:
        """
        Capture a screenshot of the entire Napari viewer, including UI elements, and return it as a PIL image.
        
        Returns:
            PIL.Image.Image: A screenshot of the current Napari viewer, or an error message if the operation fails.
        """
        def _delegated_snapshot_function(viewer: Viewer):
            # Take a screenshot of the whole Napari viewer
            screenshot = self.viewer.screenshot(canvas_only=False, flash=False)

            # Convert the screenshot (NumPy array) to a PIL image
            pil_image = fromarray(screenshot)

            return pil_image

        # Execute delegated function in napari context and return result:
        return self._execute_in_napari_context(_delegated_snapshot_function)

    def _execute_in_napari_context(self, delegated_function):
        """
        Execute a delegated function on the Napari Qt thread and return its result.
        
        If the delegated function raises an exception, returns an error message string describing the exception. If an unexpected error occurs during execution or communication, returns None.
        """
        try:

            # Send code to napari:
            self.to_napari_queue.put(delegated_function)

            # Get response:
            response = self.from_napari_queue.get()

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
