import contextlib
import traceback


class ExceptionGuard(contextlib.AbstractContextManager):

    def __init__(self, allow_print=False, print_stacktrace=False):
        self.allow_print = allow_print
        self.print_stacktrace = print_stacktrace
        self.exception_type: str = None
        self.exception_value: str = None
        self.exception_traceback = None
        self.line_number: int = None
        self.function_name: str = None
        self.filename: str = None
        self.error_string: str = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type=None, exc_value=None, _traceback=None):
        if exc_type is not None:
            self.exception_type = exc_type.__name__
            self.exception_value = exc_value
            self.exception_traceback = _traceback

            last_frame = traceback.extract_tb(_traceback)[-1]
            self.line_number = last_frame.lineno
            self.function_name = last_frame.name
            self.filename = last_frame.filename
            reason = self.exception_value.args[0] if len(
                self.exception_value.args) > 0 else ''

            self.error_string = f"Exception: {self.exception_type}"

            if len(reason.strip()) > 0:
                self.error_string += f", reason: '{reason}'"

            if len(self.function_name.strip()) > 0:
                self.error_string += f", in function: {self.function_name}"

            if len(str(self.line_number).strip()) > 0:
                self.error_string += f", at line: {self.line_number}"

            if len(self.filename.strip()) > 0:
                self.error_string += f", of file: '{self.filename}'."

            if self.print_stacktrace:
                traceback.print_exc()

            return True
