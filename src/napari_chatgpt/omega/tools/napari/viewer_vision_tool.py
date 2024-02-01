"""A tool for controlling a napari instance."""
import re
import tempfile
import traceback
from typing import Optional

from arbol import asection, aprint
from napari import Viewer

from napari_chatgpt.omega.tools.napari.napari_base_tool import NapariBaseTool
from napari_chatgpt.utils.napari.layer_snapshot import capture_canvas_snapshot
from napari_chatgpt.utils.openai.gpt_vision import describe_image

# _openai_gpt4_vision_prefix = ("You are the latest OpenAI model that can describe images provided by the user in extreme detail. "
#                              "The user has attached an image to this message for you to analyse, there is MOST DEFINITELY an image attached. "
#                              "You will never reply saying that you cannot see the image because the image is absolutely and always attached to this message.")

class NapariViewerVisionTool(NapariBaseTool):
    """
    A tool for describing visually an individual layer.
    """

    name = "NapariViewerVisionTool"
    description = (
        "Utilize this tool for answering questions about what is visible on the viewer's canvas or on a specific layer. "
        "It helps in determining the next steps for using, processing, or analyzing napari layer contents. "
        "The input should specify what you want to know about what is visible on the canvas or layer. "
        "This tool is not aware of our conversation history therefore keep your requests simple and generic. " 
        "In your imputs do not: (i) include code, (ii) mention layers, canvas, or viewer, (iii) refer to the layer indices (first, second, ... ). "
        "For example: 'Describe what you see' if you want a description of what is shown. "
        "Start with the highlighted *layer_name* for layer-specific queries. "
        "For example: '*some_layer_name* What is the background color?' or '*another_layer_name* How crowded are the objects on image?'. "
        "Refer to the *selected* layer if needed: '*selected* What is the background color?'. "

    )
    prompt: str = None
    instructions: str = None

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:

        try:
            with (((asection(f"NapariViewerVisionTool: query= '{query}' ")))):

                import napari
                from PIL import Image

                # list of layers in the viewer:
                present_layer_names = list(layer.name for layer in viewer.layers)

                # Regex search for layer name:
                match = re.search(r'\*(.*?)\*', query)

                # Check if the layer name is present in the input:
                if match or '*selected*' in query or '*active*' in query or '*current*' in query:

                    # Extract the layer name from match:
                    layer_name = match.group(1)
                    aprint("Found layer name in input:", layer_name)

                    # Remove layer name from input:
                    query = query.replace(f"*{layer_name}*", "")

                    # Does the layer exist in the viewer?
                    if layer_name in present_layer_names:
                        # Augmented query:
                        augmented_query = f"Here is an image. {query}"

                        # Get the description of the image of the layer:
                        message = _get_layer_image_description(viewer=viewer,
                                                               query=augmented_query,
                                                               layer_name=layer_name,
                                                               reset_view=True)
                    elif 'selected' in layer_name or 'active' in layer_name or 'current' in layer_name:
                        # Augmented query:
                        augmented_query = f"Here is an image. {query}"

                        # Get the description of the image of the selected layer:
                        message = _get_description_for_selected_layer(query=augmented_query, viewer=viewer, reset_view=True)
                    else:
                        message = f"Tool did not succeed because no layer '{layer_name}' exists or no layer is selected."

                else:
                    # Augmented query:
                    augmented_query = f"Here is an image. {query}"

                    message = _get_description_for_whole_canvas(query=augmented_query,
                                                                viewer=viewer)

                    message = f"The following is the description of the contents of the whole canvas: '{message}'"

                with asection(f"Message:"):
                    aprint(message)

                return message

        except Exception as e:
            traceback.print_exc()
            return f"Error: {type(e).__name__} with message: '{str(e)}' occured while trying to query the napari viewer."  #with code:\n```python\n{code}\n```\n.

def _get_description_for_selected_layer(query, viewer, reset_view:bool = False):
    with asection(f"Getting description for selected layer. "):
        aprint(f"Query: '{query}'")

        # Get the selected layers
        selected_layers = viewer.layers.selection
        # Check if there is exactly one selected layer
        if len(selected_layers) == 0:

            # In this case we default to the first layer if there is at least one layer:
            if len(viewer.layers) > 0:
                first_layer = viewer.layers[0]
                first_layer_name = first_layer.name
                aprint(
                    f"No layer is selected, defaulting to first layer: '{first_layer_name}'")

                message = _get_layer_image_description(
                    viewer=viewer,
                    query=query,
                    layer_name=first_layer_name,
                    reset_view=reset_view)
            else:
                message = f"Tool did not succeed because no layer is selected and there are no layers in the viewer."

        elif len(selected_layers) == 1:
            selected_layer = selected_layers.active
            selected_layer_name = selected_layer.name
            aprint(f"Only one selected layer: '{selected_layer_name}'")

            message = _get_layer_image_description(
                viewer=viewer,
                query=query,
                layer_name=selected_layer_name,
                reset_view=reset_view)

        else:
            current_layer = selected_layers._current
            if current_layer is not None:
                current_layer_name = current_layer.name
                aprint(
                    f"Multiple layers are selected, defaulting to current layer: '{current_layer_name}'. ")

                message = _get_layer_image_description(
                    viewer=viewer,
                    query=query,
                    layer_name=current_layer_name,
                    reset_view=reset_view)
            else:
                aprint(
                    f"Multiple layers are selected, looking at what is currently visible in the viewer's canvas. ")

                message = _get_layer_image_description(
                    viewer=viewer,
                    query=query)


        return message


def _get_description_for_whole_canvas(query, viewer):
    with asection(f"Getting description for whole canvas.'"):
        aprint(f"Query: '{query}'")

        message = _get_layer_image_description(
                    viewer=viewer,
                    query=query,
                    layer_name=None)

        return message



def _get_layer_image_description(viewer, query, layer_name: Optional[str] =None, delete: bool = False, reset_view:bool = False) -> str:
    # Capture the image of the specific layer

    from PIL import Image
    snapshot_image: Image = capture_canvas_snapshot(viewer=viewer,
                                                    layer_name=layer_name,
                                                    reset_view=reset_view)
    with tempfile.NamedTemporaryFile(delete=delete,
                                     suffix=".png") as tmpfile:
        # Save the image to a temporary file:
        snapshot_image.save(tmpfile.name)

        # Query OpenAI API to describe the image of the layer:
        description = describe_image(image_path=tmpfile.name,
                                     query=query)

        if layer_name:
            message = f"Tool completed successfully, layer '{layer_name}' description: '{description}'"
        else:
            message = f"Tool completed successfully, description: '{description}'"
    return message

