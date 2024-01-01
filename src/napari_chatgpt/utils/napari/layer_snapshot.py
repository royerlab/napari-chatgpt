from typing import Optional

from PIL import Image

from napari import Viewer


def capture_canvas_snapshot(viewer: Viewer,
                            layer_name: Optional[str] = None,
                            reset_view: Optional[bool] = True) -> Image:
    """
    Capture a snapshot of the canvas of the napari viewer with only the given layer visible.

    Parameters
    ----------
    viewer : Viewer
        The napari viewer.
    layer_name : str
        The name of the layer to capture the snapshot of. Can be None, in which case all visible layers are captured.
    reset_view : bool
        Whether to reset the view before taking the snapshot.

    Returns
    -------
    Image
        The snapshot of the canvas of the napari viewer with only the given layer visible.
    """
    # Save the state of the visibility flag of all layers:
    visibility = {layer: layer.visible for layer in viewer.layers}

    # Save the current camera view
    if reset_view:
        saved_view = {
            'center': viewer.camera.center,
            'zoom': viewer.camera.zoom,
            'angles': viewer.camera.angles
        }

        # Reset the view
        viewer.reset_view()

    # If no layer name is given, use all layers:
    if layer_name:
        # Hide all layers except for the given one:
        for layer in viewer.layers:
            layer.visible = (layer.name == layer_name)

    # Take a snapshot of the viewer canvas:
    snapshot = viewer.screenshot(canvas_only=True, flash=True)

    # Restore the original view
    if reset_view:
        viewer.camera.center = saved_view['center']
        viewer.camera.zoom = saved_view['zoom']
        viewer.camera.angles = saved_view['angles']

    # Convert array to image:
    image = Image.fromarray(snapshot)

    # Reset the visibility of all layers to their original state:
    if layer_name:
        for layer, was_visible in visibility.items():
            layer.visible = was_visible

    # Return the image:
    return image


