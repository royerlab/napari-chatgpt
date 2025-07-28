from typing import Optional

from PIL import Image
from napari import Viewer


def capture_canvas_snapshot(
    viewer: Viewer, layer_name: Optional[str] = None, reset_view: Optional[bool] = True
) -> Image:
    """
    Capture a snapshot of the napari viewer's canvas, optionally isolating a single layer and resetting the camera view.
    
    Parameters:
        layer_name (str, optional): If provided, only this layer is visible in the snapshot; otherwise, all currently visible layers are included.
        reset_view (bool, optional): If True, resets the camera view before capturing and restores it afterward.
    
    Returns:
        Image: A PIL Image of the captured viewer canvas.
    """
    # Save the state of the visibility flag of all layers:
    visibility = {layer: layer.visible for layer in viewer.layers}

    # Save the current camera view
    if reset_view:
        saved_view = {
            "center": viewer.camera.center,
            "zoom": viewer.camera.zoom,
            "angles": viewer.camera.angles,
        }

        # Reset the view
        viewer.reset_view()

    # If no layer name is given, use all layers:
    if layer_name:
        # Hide all layers except for the given one:
        for layer in viewer.layers:
            layer.visible = layer.name == layer_name

    # Take a snapshot of the viewer canvas:
    snapshot = viewer.screenshot(canvas_only=True, flash=True)

    # Restore the original view
    if reset_view:
        viewer.camera.center = saved_view["center"]
        viewer.camera.zoom = saved_view["zoom"]
        viewer.camera.angles = saved_view["angles"]

    # Convert array to image:
    image = Image.fromarray(snapshot)

    # Reset the visibility of all layers to their original state:
    if layer_name:
        for layer, was_visible in visibility.items():
            layer.visible = was_visible

    # Return the image:
    return image
