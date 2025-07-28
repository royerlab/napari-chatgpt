from pathlib import Path
from typing import Union


def format_code(code: str) -> str:
    """
    Formats a Python code string using the Black code formatter.
    
    If formatting fails due to an import or runtime error, returns the original unformatted code.
        
    Parameters:
        code (str): The Python code to format.
    
    Returns:
        str: The formatted code, or the original code if formatting fails.
    """
    try:

        from black import format_str, FileMode, InvalidInput

        # Format the code string using Black
        formatted_code_str = format_str(code, mode=FileMode())

        return formatted_code_str

    except Exception as e:
        import traceback

        print(traceback.format_exc())
        return code


def format_file(file_path: Union[str, Path]) -> None:
    """
    Format a Python source file in place using the Black code formatter.
    
    Parameters:
        file_path (Union[str, Path]): Path to the Python file to be formatted. Accepts a string or Path object.
    """

    try:
        # Ensure file_path is a Path object
        if isinstance(file_path, str):
            file_path = Path(file_path)

        # Local import to avoid polution of the global namespace:
        from black import FileMode, format_file_in_place, WriteBack

        # Format the file using Black
        format_file_in_place(
            file_path, fast=False, mode=FileMode(), write_back=WriteBack.YES
        )

    except Exception as e:
        import traceback

        print(traceback.format_exc())

    finally:
        pass
