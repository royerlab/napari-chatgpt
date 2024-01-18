from queue import Queue
from typing import Callable

import napari
import napari.viewer
from arbol import aprint, asection
from napari import Viewer
from napari.qt.threading import thread_worker

from napari_chatgpt.omega.tools.special.exception_catcher_tool import \
    enqueue_exception
from napari_chatgpt.utils.napari.napari_viewer_info import \
    get_viewer_layers_info
from napari_chatgpt.utils.python.exception_guard import ExceptionGuard


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
                code = to_napari_queue.get()
                if code is None:
                    break  # stops.
                # aprint(f"omega_napari_worker received: '{code}' from the queue.")
                yield code

        # create the worker:
        self.worker = omega_napari_worker(self.to_napari_queue,
                                          self.from_napari_queue)


    def get_viewer_description(self) -> str:

        # Setting up delegated fuction:
        delegated_function = lambda v: get_viewer_layers_info(v)

        # Send code to napari:
        self.to_napari_queue.put(delegated_function)

        # Get response:
        response = self.from_napari_queue.get()

        if isinstance(response, ExceptionGuard):
            exception_guard = response
            # raise exception_guard.exception
            return f"Error: {exception_guard.exception_type_name} with message: '{str(exception_guard.exception)}' while using tool: {self.__class__.__name__} ."

        return response


