"""A tool for opening ome-zarr files in napari"""

import queue
import sys
import traceback

from arbol import aprint, asection

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool
from napari_chatgpt.utils.python.exception_description import exception_description

# Create a queue to store exception information
exception_queue = queue.Queue()

# existing exception handler:
_original_exception_handler = sys.excepthook


# New handler:
def _uncaught_exception_handler(exctype, value, _traceback):
    # Store the exception information in the queue

    enqueue_exception(value)
    aprint(value)
    traceback.print_exc()

    # if _original_exception_handler != sys.__excepthook__:
    #     # Call the existing uncaught exception handler
    #     _original_exception_handler(exctype, value, traceback)


def enqueue_exception(exception):
    exception_queue.put(exception)


# Set the new uncaught exception handler
sys.excepthook = _uncaught_exception_handler


class ExceptionCatcherTool(BaseOmegaTool):
    """
    A tool that catches all uncaught exceptions and makes them available to Omega.
    This tool is useful for debugging and understanding issues that occur during the execution of Omega tools.
    """

    def __init__(self, **kwargs):
        """
        Initialize the ExceptionCatcherTool with a name, description, and optional prompt.
        
        Additional keyword arguments are passed to the base class initializer.
        """
        super().__init__(**kwargs)

        # Tool name and description:
        self.name = "ExceptionCatcherTool"
        self.description = (
            "This tool is usefull when the user is having problems with a widget ."
            "This tool returns information about the exception that happened. "
            "Traceback information is also provided to help find the source of the issue. "
            "Input should be the number of expeptions to report on, should be a single integer (>0). "
        )
        self.prompt: str = None

    def run_omega_tool(self, query: str = ""):

        """
        Retrieve and report a list of uncaught exceptions captured by the global exception handler.
        
        Parameters:
            query (str): Optional string representing the number of exceptions to report. If not a valid integer, all available exceptions are reported.
        
        Returns:
            str: A formatted string containing descriptions of the most recent uncaught exceptions.
        """
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
