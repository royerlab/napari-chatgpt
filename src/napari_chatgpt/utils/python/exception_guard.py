"""Context manager for catching and recording exceptions without re-raising."""

import contextlib
import traceback

from napari_chatgpt.utils.python.exception_description import exception_description


class ExceptionGuard(contextlib.AbstractContextManager):
    """Context manager that catches exceptions and stores their details.

    Any exception raised within the guarded block is suppressed and its
    details (type, value, traceback, description) are stored as attributes
    for later inspection.

    Attributes:
        exception: The exception class that was raised, or None.
        exception_type_name: Name of the exception class, or None.
        exception_value: The exception instance, or None.
        exception_traceback: The traceback object, or None.
        exception_description: Human-readable description of the error, or None.
    """

    def __init__(self, allow_print=False, print_stacktrace=True):
        """Initialize the exception guard.

        Args:
            allow_print: If True, allow print statements within the guarded
                block. Defaults to False.
            print_stacktrace: If True, print the full stacktrace when an
                exception is caught. Defaults to True.
        """
        self.allow_print = allow_print
        self.print_stacktrace = print_stacktrace
        self.exception: Exception = None
        self.exception_type_name: str = None
        self.exception_value: str = None
        self.exception_traceback = None
        self.exception_description: str = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type=None, exc_value=None, _traceback=None):
        if exc_type is not None:

            self.exception = exc_type
            self.exception_type_name = exc_type.__name__
            self.exception_value = exc_value
            self.exception_traceback = _traceback

            self.exception_description = exception_description(exc_value)

            if self.print_stacktrace:
                traceback.print_exc()

            return True
