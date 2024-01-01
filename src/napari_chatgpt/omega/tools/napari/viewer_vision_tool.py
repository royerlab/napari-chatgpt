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


class NapariViewerVisionTool(NapariBaseTool):
    """
    A tool for describing visually an individual layer.
    """

    name = "NapariViewerVisionTool"
    description = (
        "Use this tool when you want a description of what is currently visible on the viewer's canvas. "
        "This tool is usefull for deciding how to next use, process, or analyse the contents of the viewer and its layers. "
        "Input must be a request about what to focus on or pay attention to. "
        "If the input contains the emphasised name of a layer (*layer_name*) the other layers are hidden from view and only the mentioned layer is visible. "
        "For instance, you can request to 'Describe the image', where 'image' refers to the snapshot image of the layers displayed on the canvas. "
        "Or request to 'Describe the contents of image *some_layer_name*', where 'image' refers to the snapshot of layer 'some_layer_name'.  "
        "Please use the term 'image' in your input instead of 'layer' to avoid confusion. "
        "The result will be a detailed description of the visual contents of the canvas or layer. "
        "If you want to refer to the selected layer, you can refer to the *selected* layer in the input. "
        "Do NOT include code in your input. "
    )
    prompt: str = None
    instructions: str = None

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:

        try:
            with asection(f"NapariViewerVisionTool: query= '{query}' "):

                import napari
                from PIL import Image

                # list of layers in the viewer:
                present_layer_names = list(layer.name for layer in viewer.layers)

                # Regex search for layer name:
                match = re.search(r'\*(.*?)\*', query)

                # Check if the layer name is present in the input:
                if match:

                    # Extract the layer name from match:
                    layer_name = match.group(1)
                    aprint("Found layer name in input:", layer_name)

                    # Does the layer exist in the viewer?
                    if layer_name in present_layer_names:
                        # Augmented query:
                        augmented_query = f"Here is a snapshot image of the napari viewer canvas showing the contents of layer '{layer_name}'. \n" + query

                        # Get the description of the image of the layer:
                        message = _get_layer_image_description(viewer=viewer,
                                                               query=augmented_query,
                                                               layer_name=layer_name)
                    elif 'selected' in layer_name or 'active' in layer_name or 'current' in layer_name:
                        # Augmented query:
                        augmented_query = f"Here is a snapshot image of the napari viewer canvas showing only the selected layer. \n" + query

                        # Get the description of the image of the selected layer:
                        message = _get_description_for_selected_layer(query=augmented_query, viewer=viewer)
                    else:
                        message = f"Tool did not succeed because no layer '{layer_name}' exists or no layer is selected."

                else:
                    # Augmented query:
                    augmented_query = f"Here is a snapshot image of the napari viewer canvas. \n" + query

                    message = _get_description_for_selected_layer(query=augmented_query,
                                                                  viewer=viewer)

                with asection(f"Message:"):
                    aprint(message)

                return message

        except Exception as e:
            traceback.print_exc()
            return f"Error: {type(e).__name__} with message: '{str(e)}' occured while trying to query the napari viewer."  #with code:\n```python\n{code}\n```\n.

def _get_description_for_selected_layer(query, viewer):
    aprint(
        "Could not find layer name in input defaulting to selected layer")
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
                layer_name=first_layer_name)
        else:
            message = f"Tool did not succeed because no layer is selected and there are no layers in the viewer."

    elif len(selected_layers) == 1:
        selected_layer = selected_layers.active
        selected_layer_name = selected_layer.name
        aprint(f"Only one selected layer: '{selected_layer_name}'")

        message = _get_layer_image_description(
            viewer=viewer,
            query=query,
            layer_name=selected_layer_name)

    else:
        current_layer = selected_layers._current
        if current_layer is not None:
            current_layer_name = current_layer.name
            aprint(
                f"Multiple layers are selected, defaulting to current layer: '{current_layer_name}'. ")

            message = _get_layer_image_description(
                viewer=viewer,
                query=query,
                layer_name=current_layer_name)
        else:
            aprint(
                f"Multiple layers are selected, looking at what is currently visible in the viewer's canvas. ")

            message = _get_layer_image_description(
                viewer=viewer,
                query=query)


    return message


def _get_layer_image_description(viewer, query, layer_name: Optional[str] =None, delete: bool = False) -> str:
    # Capture the image of the specific layer

    from PIL import Image
    snapshot_image: Image = capture_canvas_snapshot(viewer=viewer,
                                                    layer_name=layer_name,
                                                    reset_view=False)
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

