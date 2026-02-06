from pathlib import Path


def format_code(code: str) -> str:
    """Format the code using black."""
    try:

        from black import FileMode, format_str

        # Format the code string using Black
        formatted_code_str = format_str(code, mode=FileMode())

        return formatted_code_str

    except Exception as e:
        import traceback

        print(traceback.format_exc())
        return code


def format_file(file_path: str | Path) -> None:
    """Format the file using black."""

    try:
        # Ensure file_path is a Path object
        if isinstance(file_path, str):
            file_path = Path(file_path)

        # Local import to avoid pollution of the global namespace:
        from black import FileMode, WriteBack, format_file_in_place

        # Format the file using Black
        format_file_in_place(
            file_path, fast=False, mode=FileMode(), write_back=WriteBack.YES
        )

    except Exception as e:
        import traceback

        print(traceback.format_exc())
