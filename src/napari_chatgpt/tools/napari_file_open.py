"""A tool for opening ome-zarr files in napari"""
import traceback

from napari import Viewer

from napari_chatgpt.tools.napari_base_tool import NapariBaseTool
from napari_chatgpt.utils.open_zarr_in_napari import open_in_napari


class NapariFileOpenTool(NapariBaseTool):
    """A tool for running python code in a REPL."""

    name = "NapariFileOpen"
    description = (
        "Forward to this tool requests to open image files in napari. "
        "Requests must be a newline (\\n) delimited list of local file paths or URLs to be opened."
        "This tool can open image files with these extensions: .tif, .png, .jpg, .zarr, and more..."

    )
    prompt: str = None

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:

        try:

            # Split lines:
            lines = query.splitlines()

            for line in lines:

                # Remove whitespaces:
                line = line.strip()

                # # Extract URLs from query:
                # urls = extract_urls(line)

                # add everything zarr that can be added to napari:
                # success = all(open_in_napari(viewer, url) for url in urls)

                success = open_in_napari(viewer, line)

                # Return outcome:
                if success:
                    return f"Success: query: '{query}' worked!"
                else:
                    return f"failure: one of the image files could not be opened!"

        except Exception as e:

            # If anything goes wrong:
            traceback.print_exc()
            return f"Failure: one of the image files could not be opened because of an exception: {type(e).__name__}!"
