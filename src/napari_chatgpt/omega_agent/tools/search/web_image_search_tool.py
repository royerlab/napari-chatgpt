"""Tool for searching and opening web images in the napari viewer.

Uses DuckDuckGo image search to find images matching a query, downloads
them, and loads them as layers in the napari viewer. Supports requesting
a specific number of images via parenthesized integers in the query.
"""

import traceback

import numpy
from arbol import aprint, asection
from imageio.v3 import imread
from napari import Viewer

from napari_chatgpt.omega_agent.tools.base_napari_tool import BaseNapariTool
from napari_chatgpt.utils.download.download_files import download_file_stealth
from napari_chatgpt.utils.strings.find_integer_in_parenthesis import (
    find_integer_in_parenthesis,
)
from napari_chatgpt.utils.web.duckduckgo import search_images_ddg


class WebImageSearchTool(BaseNapariTool):
    """Tool for searching and opening web images in napari.

    Searches the web for images matching a text query using DuckDuckGo,
    downloads them, and adds them as image layers in the napari viewer.
    The number of images to open can be specified in parentheses within
    the query string (e.g., 'cats (3)' opens 3 cat images).

    Attributes:
        name: Tool identifier string.
        description: Human-readable description used by the LLM agent.
        prompt: Optional prompt override (unused, defaults to None).
    """

    def __init__(self, **kwargs):
        """Initialize the WebImageSearchTool.

        Args:
            **kwargs: Keyword arguments forwarded to ``BaseNapariTool``,
                including ``notebook``, ``llm``, queue references, etc.
        """
        super().__init__(**kwargs)

        # Tool name and description:
        self.name = "WebImageSearchTool"
        self.description = (
            "Use this tool to open various types of images, such as photographs, paintings, drawings, "
            "maps, or any other kind of image, in the software called napari. "
            "Input must be a plain text web search query suitable to find the relevant images. "
            "You must specify the number of images you want to open in parentheses. "
            "For example, if the input is: 'Albert Einstein (2)' then this tool will open two images of Albert Einstein found on the web."
        )
        self.prompt: str = None

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:
        """Search for images on the web and open them in the napari viewer.

        Parses the query for an optional integer in parentheses to determine
        how many images to open, performs a DuckDuckGo image search, downloads
        the results, and adds them as image layers. Skips images that fail to
        download or decode.

        Args:
            query: Search query string, optionally containing a count in
                parentheses (e.g., 'sunset (3)').
            code: Unused; present for API compatibility with ``BaseNapariTool``.
            viewer: The napari ``Viewer`` instance to add image layers to.

        Returns:
            A status message indicating how many images were opened, or an
            error message if the search or all downloads failed.
        """
        try:

            with asection(f"WebImageSearchTool:"):
                with asection(f"Query:"):
                    aprint(query)

                # Parse the number of images to search
                result = find_integer_in_parenthesis(query)

                # Identify search query from nb of images:
                if result:
                    search_query, nb_images = result
                else:
                    search_query, nb_images = query, 1

                # Basic Cleanup:
                search_query = search_query.strip()
                nb_images = max(1, nb_images)

                # Search for image:
                results = search_images_ddg(
                    query=search_query, num_results=2 * nb_images
                )

                aprint(f"Found {len(results)} images.")

                # Extract URLs:
                urls = [r["image"] for r in results]
                with asection(f"All URLs found:"):
                    for url in urls:
                        aprint(url)

                # Limit the number of images to open to the number found:
                nb_images = min(len(urls), nb_images)

                # open each image:
                number_of_opened_images = 0
                for i, url in enumerate(urls):
                    try:
                        aprint(f"Trying to open image {i} from URL: {url}.")

                        # Download the image:
                        file_path = download_file_stealth(url)

                        if file_path is None:
                            aprint(f"Image {i} download failed (None path), skipping.")
                            continue

                        # Open the image:
                        image = imread(file_path)

                        # convert to array:
                        image_array = numpy.array(image)

                        # Add to napari:
                        viewer.add_image(image_array, name=f"image_{i}")

                        # Increment counter:
                        number_of_opened_images += 1
                        aprint(f"Image {i} opened!")

                        # Stop if we have opened enough images:
                        if number_of_opened_images >= nb_images:
                            break

                    except Exception as e:
                        # We ignore single failures:
                        aprint(f"Image {i} failed to open!")
                        traceback.print_exc()

                if number_of_opened_images > 0:
                    message = f"Opened {number_of_opened_images} images in napari out of {len(urls)} found."
                else:
                    message = f"Found {len(urls)} images, but could not open any! Probably because of a file format issue."

                with asection(f"Message:"):
                    aprint(message)

                return message

        except Exception as e:
            traceback.print_exc()
            return f"Error: {type(e).__name__} with message: '{str(e)}' occurred while trying to search the web for images with this query: '{query}'."
