import contextlib
import traceback

from napari_chatgpt.utils.python.exception_description import \
    exception_description


class ExceptionGuard(contextlib.AbstractContextManager):

    def __init__(self, allow_print=False, print_stacktrace=True):
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
