from PIL import Image

from napari import Viewer


def capture_layer_snapshot(viewer: Viewer, layer_name: str) -> Image:
    """
    Capture a snapshot of the canvas of the napari viewer with only the given layer visible.

    Parameters
    ----------
    viewer : Viewer
        The napari viewer.
    layer_name : str
        The name of the layer to capture the snapshot of.

    Returns
    -------
    Image
        The snapshot of the canvas of the napari viewer with only the given layer visible.
    """
    # Save the state of the visibility flag of all layers:
    visibility = {layer: layer.visible for layer in viewer.layers}

    # Hide all layers except for the given one:
    for layer in viewer.layers:
        layer.visible = (layer.name == layer_name)

    # Take a snapshot of the viewer canvas:
    snapshot = viewer.screenshot(canvas_only=True, flash=True)

    # Convert array to image:
    image = Image.fromarray(snapshot)

    # Reset the visibility of all layers to their original state:
    for layer, was_visible in visibility.items():
        layer.visible = was_visible

    # Return the image:
    return image


