"""Tool for opening image files in the napari viewer.

This module provides ``NapariFileOpenTool``, which accepts a newline-delimited
list of local file paths or URLs, optionally paired with a specific reader
plugin name, and opens each one in the napari viewer.  Supported formats
include .tif, .png, .jpg, .zarr, and any format for which a napari reader
plugin is available.
"""

import traceback

from arbol import aprint, asection
from napari import Viewer

from napari_chatgpt.omega_agent.tools.base_napari_tool import BaseNapariTool
from napari_chatgpt.utils.napari.open_in_napari import open_in_napari


class NapariFileOpenTool(BaseNapariTool):
    """Tool for opening image files in the napari viewer.

    Accepts a newline-delimited list of file paths or URLs.  Each entry may
    optionally specify a reader plugin in brackets, e.g.
    ``path/to/file.zarr [napari-ome-zarr]``.  The tool iterates over entries,
    attempts to open each one, and reports which files succeeded or failed.

    This tool does not use the sub-LLM code-generation pipeline; the
    ``prompt`` and ``instructions`` attributes are set to ``None``.
    """

    def __init__(self, **kwargs):
        """Initialize the file-open tool.

        Args:
            **kwargs: Forwarded to ``BaseNapariTool.__init__``.
        """
        super().__init__(**kwargs)

        self.name = "NapariFileOpenTool"
        self.description = (
            "Use this tool when you need to open image files in napari. "
            "Input must be a plain text list of local file paths or URLs to be opened. "
            "The list must be \\n delimited, i.e one entry per line. "
            "For for each file a specific napari reader plugin can be specified within brackets: 'file_path_or_url [reader_plugin_name]'. "
            "This tool can only open image files with these extensions: .tif, .png, .jpg, .zarr, and more... "
            "For example, if the input is: 'file1.tif\\nfile2.tif\\nfile3.tif' then this tool will open three images in napari. "
            "This tool cannot open text files or other non-image files. "
        )
        self.prompt: str = None
        self.instructions: str = None

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:
        """Open one or more image files in the napari viewer.

        Parses the newline-delimited query for file paths and optional reader
        plugin names, then attempts to open each file.  Returns a summary
        indicating which files were opened successfully and which failed.

        Args:
            query: Newline-delimited list of file paths / URLs (with optional
                ``[plugin_name]`` suffixes).
            code: Unused (no LLM code generation for this tool).
            viewer: The active napari viewer instance.

        Returns:
            A summary message listing opened files and any errors encountered.
        """
        with asection(f"NapariFileOpenTool:"):
            with asection(f"Query:"):
                aprint(query)

            # Files opened:
            opened_files = []

            # Errors encountered:
            encountered_errors = []

            # Split lines:
            lines = query.splitlines()

            # Remove any whitespace from the list entries:
            lines = [line.strip() for line in lines]

            for line in lines:

                # Remove whitespaces:
                line = line.strip()

                # Check if a plugin is specified:
                if "[" in line and "]" in line:
                    plugin = line[line.index("[") + 1 : line.index("]")].strip()
                    line = line[: line.index("[")].strip()
                else:
                    plugin = None

                # Try to open file:
                try:
                    aprint(f"Trying to open file: '{line}' with plugin '{plugin}'")

                    success = open_in_napari(viewer, line, plugin=plugin)

                    if success:
                        aprint(f"Successfully opened file: '{line}'. ")
                        opened_files.append(line)

                except Exception as e:
                    traceback.print_exc()
                    error_info = f"Error: '{type(e).__name__}' with message: '{str(e)}' occurred while trying to open: '{line}'."
                    encountered_errors.append(error_info)

            # Encountered errors string:
            encountered_errors_str = "\n".join(encountered_errors)

            if encountered_errors:
                aprint(
                    f"Encountered the following errors while trying to open the files:\n"
                    f"{encountered_errors_str}\n"
                )

            # Return outcome:
            if len(opened_files) == len(lines) and len(encountered_errors) == 0:
                result = f"All of the image files: '{', '.join(opened_files)}' could be successfully opened in napari. "
                aprint(result)
                return result
            elif len(opened_files) > 0 and len(encountered_errors) > 0:
                result = (
                    f"Some of the image files: '{', '.join(opened_files)}' could be successfully opened in napari.\n"
                    f"Here are the exceptions, if any, that occurred:\n"
                    f"{encountered_errors_str}.\n"
                )
                aprint(result)
                return result
            else:
                result = (
                    f"Failure: none of the image files could be opened!\n"
                    f"Here are the exceptions, if any, that occurred:\n"
                    f"{encountered_errors_str}.\n"
                )
                aprint(result)
                return result
