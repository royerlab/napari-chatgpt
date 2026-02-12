"""Utilities for extracting human-readable descriptions from Python exceptions.

Provides functions to traverse exception chains, extract traceback details,
and format concise error descriptions including the offending source line.
"""

import traceback


def exception_description(
    exception,
    include_filename: bool = False,
    include_line_number: bool = False,
) -> str:
    """Build a human-readable description of an exception's root cause.

    Args:
        exception: The exception to describe.
        include_filename: Whether to include the source filename.
        include_line_number: Whether to include the line number.

    Returns:
        A formatted string describing the error, its type, and the
        offending line of code.
    """
    info = exception_info(exception)

    description = get_exception_description_string(
        info,
        include_filename=include_filename,
        include_line_number=include_line_number,
    )

    return description


def get_exception_description_string(
    info,
    include_filename: bool = False,
    include_line_number: bool = False,
):
    """Format an exception info dict into a descriptive string.

    Args:
        info: Dictionary from ``exception_info()`` with keys 'exception_name',
            'exception_message', 'error_line', 'filename', 'line_number'.
        include_filename: Whether to append the source filename.
        include_line_number: Whether to append the line number.

    Returns:
        A formatted error description string.
    """
    name = info["exception_name"]
    message = info["exception_message"]
    line = info["error_line"]

    description = ""
    description += f"Error Message: {message} ({name})"
    if line and "code line unavailable" not in line:
        description += f" at: '{line}'"
    if include_filename and info["filename"]:
        filename = info["filename"]
        description += f", filename: '{filename}'"
    if include_line_number and info["line_number"]:
        line_number = info["line_number"]
        description += f", line Number: '{line_number}'."

    return description


def exception_info(exception) -> dict[str, str]:
    """Extract detailed information from an exception's root cause.

    Follows the exception chain to find the root cause, then extracts
    the filename, line number, offending code line, exception name,
    and exception message.

    Args:
        exception: The exception to inspect.

    Returns:
        A dict with keys: 'filename', 'line_number', 'error_line',
        'exception_name', 'exception_message'.
    """
    # We make sure we have the root cause:
    exception = find_root_cause(exception)

    # Retrieve the traceback information
    tb_entries = traceback.extract_tb(exception.__traceback__)

    # Get the filename and line number of the last entry in the traceback
    if tb_entries:
        last_entry = tb_entries[-1]
        filename = last_entry.filename
        line_number = last_entry.lineno
    else:
        filename = "<no traceback>"
        line_number = 0

    try:
        # Read the code line from the file
        with open(filename) as file:
            code_lines = file.readlines()
            error_line = code_lines[line_number - 1].strip()
    except (FileNotFoundError, IndexError):
        # File not found or line number out of range
        error_line = "<code line unavailable>"

    # Get exception name and message
    exception_name = type(exception).__name__
    exception_message = str(exception)

    # Prepare the detailed information as a dictionary
    details = {
        "filename": filename,
        "line_number": line_number,
        "error_line": error_line,
        "exception_name": exception_name,
        "exception_message": exception_message,
    }

    return details


def find_root_cause(exception, _depth=0):
    """Recursively follow the exception chain to find the root cause.

    Args:
        exception: The exception to trace.
        _depth: Internal recursion depth counter to prevent infinite loops.

    Returns:
        The root-cause exception (the deepest ``__cause__``).
    """
    if _depth > 100 or exception.__cause__ is None:
        return exception
    else:
        return find_root_cause(exception.__cause__, _depth + 1)
