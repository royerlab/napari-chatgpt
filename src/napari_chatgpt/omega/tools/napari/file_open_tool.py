"""A tool for opening ome-zarr files in napari"""
import traceback

from arbol import asection, aprint
from napari import Viewer

from napari_chatgpt.omega.tools.napari.napari_base_tool import NapariBaseTool
from napari_chatgpt.utils.napari.open_in_napari import open_in_napari


class NapariFileOpenTool(NapariBaseTool):
    """A tool for running python code in a REPL."""

    name = "NapariFileOpenTool"
    description = (
        "Use this tool when you need to open image files in napari. "
        "Input must be a plain text list of local file paths or URLs to be opened. "
        "The list must be \\n delimited, i.e one entry per line. "
        "This tool can only open image files with these extensions: .tif, .png, .jpg, .zarr, and more... "
        "For example, if the input is: 'file1.tif\\nfile2.tif\\nfile3.tif' then this tool will open three images in napari. "
        "This tool cannot open text files or other non-image files. "
    )
    prompt: str = None
    instructions: str = None

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:

        with asection(f"NapariFileOpenTool: query= {query} "):

            # Split lines:
            lines = query.splitlines()

            # Files opened:
            opened_files = []

            # Errors encountered:
            encountered_errors = []

            for line in lines:

                # Remove whitespaces:
                line = line.strip()

                aprint(f"Trying to open file: '{line}' ")

                # Try to open file:
                try:
                    success = open_in_napari(viewer, line)

                    if success:
                        aprint(f"Successfully opened file: '{line}'. ")
                        opened_files.append(line)

                except Exception as e:
                    traceback.print_exc()
                    error_info = f"Error: '{type(e).__name__}' with message: '{str(e)}' occurred while trying to open: '{line}'."
                    encountered_errors.append(error_info)

            # Encountered errors string:
            encountered_errors_str = '\n'.join(encountered_errors)

            aprint(
                f"Encountered the following errors while trying to open the files:\n" \
                f"{encountered_errors_str}\n")

            # Return outcome:
            if len(opened_files) == len(lines):
                result = f"All of the image files: '{', '.join(opened_files)}' could be successfully opened in napari. "
                aprint(result)
                return result
            elif len(opened_files) > 0:
                result = f"Some of the image files: '{', '.join(opened_files)}' could be successfully opened in napari.\n" \
                         f"Here are the exceptions, if any, that occurred:\n" \
                         f"{encountered_errors_str}.\n"
                aprint(result)
                return result
            else:
                result = f"Failure: none of the image files could not be opened!\n" \
                         f"Here are the exceptions, if any, that occurred:\n" \
                         f"{encountered_errors_str}.\n"
                aprint(result)
                return result
