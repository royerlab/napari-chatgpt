"""Utilities for formatting Python code and files using Black."""

from pathlib import Path


def format_code(code: str) -> str:
    """Format a Python code string using Black.

    Args:
        code: Python source code to format.

    Returns:
        The formatted code string, or the original code if formatting fails.
    """
    try:

        from black import Mode, format_str

        # Format the code string using Black
        formatted_code_str = format_str(code, mode=Mode())

        return formatted_code_str

    except Exception as e:
        import traceback

        print(traceback.format_exc())
        return code


def format_file(file_path: str | Path) -> None:
    """Format a Python file in-place using Black.

    Args:
        file_path: Path to the Python file to format. Accepts both
            string paths and ``pathlib.Path`` objects.
    """

    try:
        # Ensure file_path is a Path object
        if isinstance(file_path, str):
            file_path = Path(file_path)

        # Local import to avoid pollution of the global namespace:
        from black import Mode, WriteBack, format_file_in_place

        # Format the file using Black
        format_file_in_place(
            file_path, fast=False, mode=Mode(), write_back=WriteBack.YES
        )

    except Exception as e:
        import traceback

        print(traceback.format_exc())
