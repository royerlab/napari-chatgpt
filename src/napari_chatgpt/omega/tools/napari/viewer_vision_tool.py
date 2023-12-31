"""A tool for controlling a napari instance."""
import re
import tempfile
import traceback

from arbol import asection, aprint
from napari import Viewer

from napari_chatgpt.omega.tools.napari.napari_base_tool import NapariBaseTool
from napari_chatgpt.utils.napari.layer_snapshot import capture_layer_snapshot
from napari_chatgpt.utils.openai.gpt_vision import describe_image


class NapariViewerVisionTool(NapariBaseTool):
    """
    A tool for describing visually an individual layer.
    """

    name = "NapariViewerVisionTool"
    description = (
        "Use this tool when you want a visual description of a specific layer present in the napari viewer. "
        "Input must be a request about what to focus on or pay attention to in the image, and must contain the name of the layer in bold. "
        "For instance, you can request to 'Describe the contents of layer *some_layer_name*'. "
        "The result will be a detailed description of the visual contents of the image of the layer."
        "Do NOT include code in your input."
    )
    prompt: str = None
    instructions: str = None

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:

        try:
            with asection(f"NapariViewerVisionTool: layer= {query} "):

                import napari
                from PIL import Image

                # Regex search for layer name:
                match = re.search(r'\*(.*?)\*', query)

                if match:

                    # Extract the layer name from match:
                    layer_name = match.group(1)
                    aprint("Extracted layer name:", layer_name)

                    # Capture the image of the specific layer
                    snapshot_image_array = capture_layer_snapshot(viewer=viewer,
                                                         layer_name=layer_name)

                    # Convert to a PIL Image
                    snapshot_image = Image.fromarray(snapshot_image_array)

                    with tempfile.NamedTemporaryFile(delete=True,
                                                     suffix=".png") as tmpfile:

                        # Save the image to a temporary file:
                        snapshot_image.save(tmpfile.name)

                        # Query OpenAI API to describe the image of the layer:
                        description = describe_image(image_path=tmpfile.name,
                                       query=query)

                        message = f"Tool completed successfully, layer '{layer_name}' description: '{description}'"

                else:
                    message = f"Tool did not succeed because the layer name could not be found in input: '{query}'"

                with asection(f"Message:"):
                    aprint(message)

                return message

        except Exception as e:
            traceback.print_exc()
            return f"Error: {type(e).__name__} with message: '{str(e)}' occured while trying to query the napari viewer."  #with code:\n```python\n{code}\n```\n.

