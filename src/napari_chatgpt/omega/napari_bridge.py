from queue import Queue
from typing import Callable

import napari
import napari.viewer
from PIL.Image import fromarray
from arbol import aprint, asection
from napari import Viewer
from napari.qt.threading import thread_worker

from napari_chatgpt.omega.tools.special.exception_catcher_tool import \
    enqueue_exception
from napari_chatgpt.utils.napari.napari_viewer_info import get_viewer_info
from napari_chatgpt.utils.notebook.jupyter_notebook import JupyterNotebookFile
from napari_chatgpt.utils.python.exception_guard import ExceptionGuard

# global Variable to exchange information with the viewer:
_viewer_info = None

def _set_viewer_info(viewer_info):
    global _viewer_info
    _viewer_info = viewer_info

def _get_viewer_info():
    global _viewer_info
    return _viewer_info

class NapariBridge():

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
                        f"Exception while executing on napari's QT thread:\n{guard.exception_description}")
                    self.from_napari_queue.put(guard)
                    enqueue_exception(guard.exception_value)

        @thread_worker(connect={'yielded': qt_code_executor})
        def omega_napari_worker(to_napari_queue: Queue,
                                from_napari_queue: Queue):
            while True:

                # get code from the queue:
                code = to_napari_queue.get()

                # execute code on napari's QT thread:
                if code is None:
                    break  # stops.

                yield code

        # create the worker:
        self.worker = omega_napari_worker(self.to_napari_queue,
                                          self.from_napari_queue)


    def get_viewer_info(self) -> str:

        # Setting up delegated function:
        delegated_function = lambda v: get_viewer_info(v)

        return self._execute_in_napari_context(delegated_function)


    def take_snapshot(self):

        # Delegated function:
        def _delegated_snapshot_function(viewer: Viewer):

            # Take a screenshot of the whole Napari viewer
            screenshot = self.viewer.screenshot(canvas_only=False, flash=False)

            # Convert the screenshot (NumPy array) to a PIL image
            pil_image = fromarray(screenshot)

            return pil_image

        # Execute delegated function in napari context and return result:
        return self._execute_in_napari_context(_delegated_snapshot_function)


    def _execute_in_napari_context(self, delegated_function):
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





