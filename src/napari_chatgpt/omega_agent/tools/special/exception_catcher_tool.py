"""Tool for catching, queuing, and reporting uncaught exceptions.

Installs a custom ``sys.excepthook`` that captures unhandled exceptions
into a thread-safe queue. The Omega agent can then query this tool to
retrieve detailed exception descriptions including tracebacks, which is
useful for automated debugging workflows.
"""

import queue
import sys
import traceback

from arbol import aprint, asection

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool
from napari_chatgpt.utils.python.exception_description import (
    exception_description,
)

# Thread-safe queue that accumulates unhandled exceptions.
exception_queue = queue.Queue()


def _uncaught_exception_handler(exctype, value, _traceback):
    """Custom ``sys.excepthook`` that enqueues exceptions for later retrieval.

    Args:
        exctype: The exception class.
        value: The exception instance.
        _traceback: The traceback object.
    """
    enqueue_exception(value)
    aprint(value)
    traceback.print_exc()


def enqueue_exception(exception):
    """Add an exception to the global exception queue.

    Args:
        exception: The exception instance to enqueue.
    """
    exception_queue.put(exception)


class ExceptionCatcherTool(BaseOmegaTool):
    """Tool that captures uncaught exceptions and reports them to the agent.

    On initialization, replaces ``sys.excepthook`` with a custom handler
    that stores exceptions in a module-level queue. When invoked, drains
    the queue and returns formatted exception descriptions with tracebacks.

    Attributes:
        name: Tool identifier string.
        description: Human-readable description used by the LLM agent.
    """

    def __init__(self, **kwargs):
        """Initialize the ExceptionCatcherTool and install the exception hook.

        Replaces ``sys.excepthook`` so that all uncaught exceptions are
        captured into ``exception_queue`` for later retrieval.

        Args:
            **kwargs: Keyword arguments forwarded to ``BaseOmegaTool``.
        """
        super().__init__(**kwargs)

        # Install the uncaught exception handler:
        self._original_excepthook = sys.excepthook
        sys.excepthook = _uncaught_exception_handler

        # Tool name and description:
        self.name = "ExceptionCatcherTool"
        self.description = (
            "This tool is useful when uncaught exceptions have occurred. "
            "It returns information about exceptions including traceback "
            "details to help find the source of the issue. "
            "Input should be the number of exceptions to report on, "
            "should be a single integer (>0)."
        )

    def run_omega_tool(self, query: str = ""):
        """Retrieve and format queued uncaught exceptions.

        Args:
            query: A string containing the number of exceptions to report.
                If not a valid integer, all queued exceptions are returned.

        Returns:
            A formatted string listing exception descriptions, or a message
            indicating no exceptions were recorded.
        """
        with asection("ExceptionCatcherTool:"):

            if exception_queue.qsize() == 0:
                return "No exceptions recorded."

            text = "Here is the list of exceptions that occurred:\n\n"
            text += "```\n"

            try:
                # We try to convert the input to an integer:
                number_of_exceptions = int(query.strip())
            except Exception:
                # If the input is not an integer, report all:
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
