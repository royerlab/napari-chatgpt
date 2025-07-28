"""A tool for controlling a napari instance."""

import re
import tempfile
import traceback
from typing import Optional

from arbol import asection, aprint
from napari import Viewer

from napari_chatgpt.omega_agent.tools.base_napari_tool import BaseNapariTool
from napari_chatgpt.utils.napari.layer_snapshot import capture_canvas_snapshot
from napari_chatgpt.utils.llm.vision import describe_image


class NapariViewerVisionTool(BaseNapariTool):
    """
    A tool for describing visually an individual layer.
    """

    def __init__(self, vision_model_name: str, **kwargs):
        """
        Initialize a NapariViewerVisionTool for describing napari viewer contents using a specified vision model.
        
        Parameters:
            vision_model_name (str): Name of the vision model to use for generating image descriptions.
            **kwargs: Additional keyword arguments forwarded to the base class.
        """

        super().__init__(**kwargs)

        self.name = "NapariViewerVisionTool"
        self.description = (
            "Utilize this tool for answering questions about what is visible on the viewer's canvas or on a specific layer. "
            "It helps in determining the next steps for using, processing, or analyzing napari layer contents. "
            "The input should specify what you want to know about what is visible on the canvas or layer. "
            "This tool is not aware of our conversation history therefore keep your requests simple and generic. "
            "In your inputs do not: (i) include code, (ii) mention layers, canvas, or viewer, (iii) refer to the layer indices (first, second, ... ). "
            "For example: 'Describe what you see' if you want a description of what is shown. "
            "Start with the highlighted *layer_name* for layer-specific queries. "
            "For example: '*some_layer_name* What is the background color?' or '*another_layer_name* How crowded are the objects on image?'. "
            "Refer to the *selected* layer if needed: '*selected* What is the background color?'. "
        )
        self.prompt: str = None
        self.instructions: str = None

        self.vision_model_name = vision_model_name

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:

        """
        Processes a textual query to describe the contents of a napari viewer or a specific layer using a vision model.
        
        Analyzes the query to determine if it references a specific layer, the selected/active/current layer, or the entire canvas. Extracts the relevant image, generates a description using the specified vision model, and returns the result. If the query references a non-existent layer, returns an error message. Handles exceptions by returning an error message with details.
        try:
            with asection(f"NapariViewerVisionTool:"):
                with asection(f"Query:"):
                    aprint(query)

                import napari
                from PIL import Image

                # list of layers in the viewer:
                present_layer_names = list(layer.name for layer in viewer.layers)

                # Regex search for layer name:
                match = re.search(r"\*(.*?)\*", query)

                # If there is no match, look for words that start with '*':
                if not match:
                    # This sometimes happens if the LLM gets confused about teh exact syntax requested:

                    # We find a match with just one star '*' and a word:
                    match = re.search(r"\*(.*?)[\s]+", query)

                    # If there is match, add the missing '*' at the end:
                    if match:
                        query = query.replace(match.group(1), f"{match.group(1)}*")

                # Check if the layer name is present in the input:
                if (
                    match
                    or "*selected*" in query
                    or "*active*" in query
                    or "*current*" in query
                ):

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
                        message = _get_layer_image_description(
                            viewer=viewer,
                            query=augmented_query,
                            layer_name=layer_name,
                            reset_view=True,
                        )
                    elif (
                        "selected" in layer_name
                        or "active" in layer_name
                        or "current" in layer_name
                    ):
                        # Augmented query:
                        augmented_query = f"Here is an image. {query}"

                        # Get the description of the image of the selected layer:
                        message = _get_description_for_selected_layer(
                            query=augmented_query,
                            viewer=viewer,
                            vision_model_name=self.vision_model_name,
                            reset_view=True,
                        )
                    else:
                        message = f"Tool did not succeed because no layer '{layer_name}' exists or no layer is selected."

                else:
                    # Augmented query:
                    augmented_query = f"Here is an image. {query}"

                    message = _get_description_for_whole_canvas(
                        query=augmented_query,
                        viewer=viewer,
                        vision_model_name=self.vision_model_name,
                    )

                    message = f"The following is the description of the contents of the whole canvas: '{message}'"

                with asection(f"Message:"):
                    aprint(message)

                return message

        except Exception as e:
            traceback.print_exc()
            return f"Error: {type(e).__name__} with message: '{str(e)}' occured while trying to query the napari viewer."  # with code:\n```python\n{code}\n```\n.


def _get_description_for_selected_layer(
    query, viewer, vision_model_name: str, reset_view: bool = False
):
    """
    Generate a description of the currently selected layer in the napari viewer using a specified vision model.
    
    If no layer is selected but layers exist, defaults to the first layer. If multiple layers are selected, uses the current layer if available; otherwise, describes the visible canvas. Returns an error message if no layers are present.
    
    Parameters:
        query (str): The textual prompt or question to guide the image description.
        vision_model_name (str): The name of the vision model to use for generating the description.
        reset_view (bool, optional): Whether to reset the viewer's view before capturing the image. Defaults to False.
    
    Returns:
        str: The generated description or an error message.
    """
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
                    f"No layer is selected, defaulting to first layer: '{first_layer_name}'"
                )

                message = _get_layer_image_description(
                    viewer=viewer,
                    query=query,
                    layer_name=first_layer_name,
                    reset_view=reset_view,
                )
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
                reset_view=reset_view,
            )

        else:
            current_layer = selected_layers._current
            if current_layer is not None:
                current_layer_name = current_layer.name
                aprint(
                    f"Multiple layers are selected, defaulting to current layer: '{current_layer_name}'. "
                )

                message = _get_layer_image_description(
                    viewer=viewer,
                    query=query,
                    layer_name=current_layer_name,
                    reset_view=reset_view,
                )
            else:
                aprint(
                    f"Multiple layers are selected, looking at what is currently visible in the viewer's canvas. "
                )

                message = _get_layer_image_description(viewer=viewer, query=query)

        return message


def _get_description_for_whole_canvas(query, viewer, vision_model_name):
    """
    Generate a description of the entire napari viewer canvas using the specified vision model.
    
    Parameters:
        query: The textual prompt or question to guide the image description.
        vision_model_name: The name of the vision model to use for generating the description.
    
    Returns:
        A string containing the generated description of the whole canvas.
    """
    with asection(f"Getting description for whole canvas.'"):
        aprint(f"Query: '{query}'")

        message = _get_layer_image_description(
            viewer=viewer,
            query=query,
            vision_model_name=vision_model_name,
            layer_name=None,
        )

        return message


def _get_layer_image_description(
    viewer,
    query,
    vision_model_name: str,
    layer_name: Optional[str] = None,
    delete: bool = False,
    reset_view: bool = False,
) -> str:
    # Capture the image of the specific layer

    """
    Generates a textual description of a specified napari layer or the entire canvas using a vision model.
    
    Captures a snapshot of the given layer (or the whole canvas if no layer is specified), saves it as a temporary PNG file, and uses the specified vision model to generate a description based on the provided query.
    
    Parameters:
        query (str): The textual prompt or question to guide the image description.
        vision_model_name (str): The name of the vision model to use for generating the description.
        layer_name (Optional[str]): The name of the layer to describe. If None, describes the entire canvas.
        delete (bool): Whether to delete the temporary image file after use.
        reset_view (bool): Whether to reset the viewer's view before capturing the snapshot.
    
    Returns:
        str: A message containing the generated description, including the layer name if specified.
    """
    from PIL import Image

    snapshot_image: Image = capture_canvas_snapshot(
        viewer=viewer, layer_name=layer_name, reset_view=reset_view
    )
    with tempfile.NamedTemporaryFile(delete=delete, suffix=".png") as tmpfile:
        # Save the image to a temporary file:
        snapshot_image.save(tmpfile.name)

        # Query OpenAI API to describe the image of the layer:
        description = describe_image(
            image_path=tmpfile.name, query=query, model_name=vision_model_name
        )

        if layer_name:
            message = f"Tool completed successfully, layer '{layer_name}' description: '{description}'"
        else:
            message = f"Tool completed successfully, description: '{description}'"
    return message
