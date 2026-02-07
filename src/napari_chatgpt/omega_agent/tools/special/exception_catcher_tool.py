"""A tool for opening ome-zarr files in napari"""

import queue
import sys
import traceback

from arbol import aprint, asection

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool
from napari_chatgpt.utils.python.exception_description import exception_description

# Create a queue to store exception information
exception_queue = queue.Queue()


def _uncaught_exception_handler(exctype, value, _traceback):
    # Store the exception information in the queue
    enqueue_exception(value)
    aprint(value)
    traceback.print_exc()


def enqueue_exception(exception):
    exception_queue.put(exception)


class ExceptionCatcherTool(BaseOmegaTool):
    """
    A tool that catches all uncaught exceptions and makes them available to Omega.
    This tool is useful for debugging and understanding issues that occur during the execution of Omega tools.
    """

    def __init__(self, **kwargs):
        """
        Initialize the ExceptionCatcherTool.

        Parameters
        ----------
        kwargs: dict
            Additional keyword arguments to pass to the base class.
            This can include parameters like `notebook`, etc.
        """
        super().__init__(**kwargs)

        # Install the uncaught exception handler:
        self._original_excepthook = sys.excepthook
        sys.excepthook = _uncaught_exception_handler

        # Tool name and description:
        self.name = "ExceptionCatcherTool"
        self.description = (
            "This tool is useful when the user is having problems with a widget ."
            "This tool returns information about the exception that happened. "
            "Traceback information is also provided to help find the source of the issue. "
            "Input should be the number of exceptions to report on, should be a single integer (>0)."
        )
        self.prompt: str = None

    def run_omega_tool(self, query: str = ""):

        with asection("ExceptionCatcherTool:"):

            text = "Here is the list of exceptions that occurred:\n\n"
            text += "```\n"

            try:
                # We try to convert the input to an integer:
                number_of_exceptions = int(query.strip())
            except Exception as e:
                # If the input is not an integer, or anything else goes wrong, we set the number of exceptions to the maximum:
                number_of_exceptions = exception_queue.qsize()

            # ensure that the number of exceptions is strictly positive:
            number_of_exceptions = max(number_of_exceptions, 1)

            while exception_queue.qsize() > 0 and number_of_exceptions > 0:
                value = exception_queue.get_nowait()

                description = exception_description(value)

                text += description

                aprint(description)

                number_of_exceptions -= 1

            text += "```\n"

            return text
