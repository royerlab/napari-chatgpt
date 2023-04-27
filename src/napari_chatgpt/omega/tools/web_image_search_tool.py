import re
import traceback

import numpy
from imageio.v3 import imread
from napari import Viewer

from napari_chatgpt.omega.tools.napari_base_tool import NapariBaseTool
from napari_chatgpt.utils.duckduckgo import search_images_ddg


class WebImageSearchTool(NapariBaseTool):
    """A tool for running python code in a REPL."""

    name = "WebImageSearchTool"
    description = (
        "Useful for when you need to search on the web for photographs, paintings, drawings, maps or any other kind of image, and open them in napari."
        "Provide a plain text query and the number of images from the top results (default=1)."
        "Use this simple two part format for forwarded requests to WebImageSearchTool: <query> | <nb images> "
    )
    prompt:str = None

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:

        try:
            # Split query:
            search_query, nb_images_str = query.split('|')

            # Basic Cleanup:
            search_query = search_query.strip()
            nb_images_str=nb_images_str.strip()

            # More advanced cleanup:
            search_query = re.sub(r"[^a-zA-Z0-9]", "", search_query)
            nb_images_str = re.sub(r"[^0-9]", "", nb_images_str)

            # Search for image:
            results = search_images_ddg(query=search_query)

            # Extract URLs:
            urls = [r['image'] for r in results]

            # Parse number of images:
            try:
                nb_images = min(len(urls), int(nb_images_str))
            except:
                traceback.print_exc()
                nb_images = 1

            # Keep only the required number of urls:
            urls = urls[:nb_images]

            for url in urls:
                image = imread(url)
                image_array = numpy.array(image)
                viewer.add_image(image_array)

            return f"Success: searched, found and opened {len(urls)} images !"

        except Exception as e:

            # If anything goes wrong:
            traceback.print_exc()
            return f"Failure: one of the image files could not be opened because of an exception: {type(e).__name__}!"


