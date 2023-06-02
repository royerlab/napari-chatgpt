import traceback
from typing import Dict


def exception_description(exception,
                          include_filename: bool = False,
                          include_line_number: bool = False) -> str:
    info = exception_info(exception)

    description = get_exception_description_string(info,
                                                   include_filename=include_filename,
                                                   include_line_number=include_line_number)

    return description


def get_exception_description_string(info,
                                     include_filename: bool = False,
                                     include_line_number: bool = False,
                                     ):

    name = info['exception_name']
    message = info['exception_message']
    line = info['error_line']

    description = f""
    description += f"Error Message: {message} ({name})"
    if line and 'code line unavailable' not in line:
        description += f" at: '{line}'"
    if include_filename and info['filename']:
        filename = info['filename']
        description += f", filename: '{filename}'"
    if include_line_number and info['line_number']:
        line_number = info['line_number']
        description += f", line Number: '{line_number}'."

    return description


def exception_info(exception) -> Dict[str, str]:
    # We make sure we have the root cause:
    exception = find_root_cause(exception)

    # Retrieve the traceback information
    tb_entries = traceback.extract_tb(exception.__traceback__)

    # Get the filename and line number of the last entry in the traceback
    last_entry = tb_entries[-1]
    filename = last_entry.filename
    line_number = last_entry.lineno

    try:
        # Read the code line from the file
        with open(filename, "r") as file:
            code_lines = file.readlines()
            error_line = code_lines[line_number - 1].strip()
    except FileNotFoundError:
        # File not found error handling
        error_line = "<code line unavailable - file not found>"

    # Get exception name and message
    exception_name = type(exception).__name__
    exception_message = str(exception)

    # Prepare the detailed information as a dictionary
    details = {
        'filename': filename,
        'line_number': line_number,
        'error_line': error_line,
        'exception_name': exception_name,
        'exception_message': exception_message
    }

    return details


def find_root_cause(exception):
    if exception.__cause__ is None:
        return exception
    else:
        return find_root_cause(exception.__cause__)
