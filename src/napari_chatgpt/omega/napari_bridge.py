from queue import Queue
from typing import Callable

import napari
import napari.viewer
from arbol import aprint, asection
from napari import Viewer
from napari.qt.threading import thread_worker

from napari_chatgpt.utils.exception_guard import ExceptionGuard


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

                if guard.exception_type:
                    aprint(
                        f"Error while executing on napari's QT thread:\n{guard.error_string}")
                    self.from_napari_queue.put(guard.error_string)

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
