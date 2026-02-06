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
    """
    A tool for searching and opening images from the web in napari.
    This tool can be used to find and open images such as photographs, paintings, drawings, maps, or any other kind of image.
    """

    def __init__(self, **kwargs):
        """
        Initialize the WebImageSearchTool.

        Parameters
        ----------
        kwargs: dict
            Additional keyword arguments to pass to the base class.
            This can include parameters like `notebook`, `fix_bad_calls`, etc.
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
        """Run the code and return the result.
        Parameters
        ----------
        query : str
            The query to search for images.
        code : str
            The code to run.
        viewer : Viewer
            The napari viewer to add the images to.
        Returns
        -------
        str
            The result of running the code. This will be printed to the user.

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
