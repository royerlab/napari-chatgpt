import traceback

import numpy
from imageio.v3 import imread
from napari import Viewer

from napari_chatgpt.omega.tools.machinery.napari_base_tool import NapariBaseTool
from napari_chatgpt.utils.strings.find_integer_in_parenthesis import \
    find_integer_in_parenthesis
from napari_chatgpt.utils.web.duckduckgo import search_images_ddg


class WebImageSearchTool(NapariBaseTool):
    """A tool for running python code in a REPL."""

    name = "WebImageSearchTool"
    description = (
        "Useful when you need to open in napari: photographs, paintings, drawings, "
        "maps or any other kind of image, and open them in napari. "
        "The images are found by conducting a web search. "
        "Provide a plain text query and the number of images to open in parenthesis, for example: <query> (2) for two images."
    )
    prompt: str = None

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:

        try:
            # Split query:
            result = find_integer_in_parenthesis(query)

            if result:
                search_query, nb_images = result
            else:
                search_query, nb_images = query, 1

            # Basic Cleanup:
            search_query = search_query.strip()
            nb_images = max(1, nb_images)

            # Search for image:
            results = search_images_ddg(query=search_query)

            # Extract URLs:
            urls = [r['image'] for r in results]

            # Parse number of images:
            try:
                nb_images = min(len(urls), int(nb_images))
            except:
                traceback.print_exc()
                nb_images = 1

            # Keep only the required number of urls:
            urls = urls[:nb_images]

            number_of_opened_images = 0
            for url in urls:
                try:
                    image = imread(url)
                    image_array = numpy.array(image)
                    viewer.add_image(image_array)
                    number_of_opened_images += 1
                except Exception as e:
                    # We ignore single failures:
                    traceback.print_exc()

            if number_of_opened_images > 0:
                return f"Success: searched, found {len(urls)} images, and opened {number_of_opened_images} !"
            else:
                return f"Failure: searched, found {len(urls)} images, but could not open any !"

        except Exception as e:

            # If anything goes wrong:
            traceback.print_exc()
            return f"Failure: one of the image files could not be opened because of an exception: {type(e).__name__}!"
