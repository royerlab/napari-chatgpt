import numpy
from napari.layers import Image, Labels, Points, Vectors, Tracks, Surface
from napari.utils.transforms import Affine


def get_viewer_info(viewer):
    """
    Return a formatted string summarizing the current state and layers of a Napari viewer.
    
    The output includes viewer settings and detailed information about each layer, wrapped in a markdown-style code block.
    """
    info = "```viewer_info\n"
    info += get_viewer_state(viewer)
    info += get_viewer_layers_info(viewer)
    info += "```\n"

    return info


def get_viewer_state(viewer):
    """
    Return a formatted string summarizing the current state of a Napari viewer, excluding layer details.
    
    The summary includes camera settings, canvas size, grid mode, display mode (2D or 3D), theme, status message, and the currently selected layer.
    """

    # Camera settings
    camera = viewer.camera
    camera_info = {
        "position": camera.center,
        "zoom": camera.zoom,
        "view angle": camera.angles,
        "perspective": camera.perspective,
    }

    # Canvas size
    canvas_size = viewer.window.qt_viewer.canvas.size

    # Grid mode status
    grid_mode = viewer.grid.enabled

    # Display mode
    display_mode = "3D" if viewer.dims.ndisplay == 3 else "2D"

    # Viewer theme
    theme = viewer.theme

    # Status information
    status = viewer.status

    # Selected layer:
    selected_layer = viewer.layers.selection.active
    if selected_layer is None:
        selected_layer = "*no layer selected*"

    # Formatting the information into a string
    description = (
        # Existing description format
        f"Napari viewer state:\n"
        f"  Camera Settings:\n"
        f"    Position: {camera_info['position']}\n"
        f"    Zoom: {camera_info['zoom']}\n"
        f"    View Angle: {camera_info['view angle']}\n"
        f"    Perspective: {camera_info['perspective']}\n"
        f"  Canvas Size: {canvas_size}\n"
        f"  Grid Mode: {'Enabled' if grid_mode else 'Disabled'}\n"
        f"  Display Mode: {display_mode}\n"
        f"  Theme: {theme}\n"
        f"  Status: {status}\n"
        f"  Selected Layer: {selected_layer}\n"
        "\n"
    )

    return description


def get_viewer_layers_info(
    viewer, max_layers: int = 20, max_layers_with_details: int = 4
):
    """
    Return a formatted summary of layers in a Napari viewer, including detailed information for the most recent layers.
    
    Parameters:
        max_layers (int): Maximum number of layers to include in the summary.
        max_layers_with_details (int): Number of most recent layers to include with detailed information.
    
    Returns:
        str: A formatted string describing up to `max_layers` layers, with extra details for the last `max_layers_with_details` layers. If no layers are present, indicates this in the output.
    """

    layer_descriptions = []

    layers = viewer.layers[len(viewer.layers) - max_layers :]

    number_of_layers = len(layers)

    for index, layer in enumerate(layers):
        layer_info = layer_description(
            viewer, layer, details=index >= number_of_layers - max_layers_with_details
        )

        # Formatting the layer information
        description = f"  Layer {index}: {layer.name} (Type: {layer_info['Type']})\n"
        for key, value in layer_info.items():
            description += f"    {key}: {value}\n"
        layer_descriptions.append(description)

    info_text = "Layers:\n"
    if len(layer_descriptions) > 0:
        info_text += "\n".join(layer_descriptions)
    else:
        info_text += "  No layers are currently present in the viewer! \n"

    return info_text


def layer_description(viewer, layer, details: bool = True):
    """
    Return a dictionary summarizing the properties of a Napari layer, including type-specific and detailed attributes.
    
    Parameters:
        layer: The Napari layer to describe.
        details (bool): If True, include additional properties such as opacity, blending, transforms, and type-specific details.
    
    Returns:
        dict: A dictionary containing general and, if requested, detailed information about the layer's properties.
    """
    layer_info = {
        "Type": type(layer).__name__,
        "Name": layer.name,
        "Visible": layer.visible,
    }

    if details:
        layer_info |= {
            "Opacity": layer.opacity,
            "Blending": layer.blending,
            "Scale": layer.scale,
            "Translate": layer.translate,
            "Rotation": array_to_single_line_string(layer.rotate),
            "Shear": array_to_single_line_string(layer.shear),
            "Affine": affine_to_single_line_string(layer.affine),
        }

    # Handling specific attributes based on layer type
    if isinstance(layer, Points):
        layer_info |= {
            "Number of points": len(layer.data),
            "Point Data Type": layer.data.dtype,
        }

        if details:
            layer_info |= {
                "Point Data Class": layer.data.__class__,
                "Symbol": layer.symbol,
                "Size": layer.size,
            }

    elif isinstance(layer, Image):
        layer_info |= {
            "Image Shape": layer.data.shape,
            "Image Data Type": layer.data.dtype,
        }

        if details:
            layer_info |= {
                "Image Data Class": layer.data.__class__,
                "Multiscale": layer.multiscale,
                "Interpolation": (
                    layer.interpolation2d
                    if viewer.dims.ndisplay == 2
                    else layer.interpolation3d
                ),
                "Rendering": layer.rendering,
            }

    elif isinstance(layer, Tracks):
        layer_info |= {
            "Number of Tracks": len(layer.data),
            "Track Data Type": layer.data.dtype,
        }

        if details:
            layer_info |= {
                "Track Data Class": layer.data.__class__,
            }

    elif isinstance(layer, Labels):
        unique_labels = numpy.unique(layer.data)
        layer_info |= {
            "Number of Labels": len(unique_labels) - (1 if 0 in unique_labels else 0),
            "Labels Data Type": layer.data.dtype,
        }

        if details:
            layer_info |= {
                "Labels Data Class": layer.data.__class__,
            }

    elif isinstance(layer, Vectors):
        layer_info |= {
            "Number of Vectors": len(layer.data),
            "Vectors Data Type": layer.data.dtype,
        }

        if details:
            layer_info |= {
                "Vectors Data Class": layer.data.__class__,
            }

    elif isinstance(layer, Surface):
        vertices, faces, values = layer.data
        layer_info |= {
            "Number of Vertices": len(vertices),
            "Number of Faces": len(faces),
            "Number of Values": len(values),
        }

        if details:
            pass

    return layer_info


def affine_to_single_line_string(affine):
    """
    Converts a Napari Affine object to a single-line string representation.

    Parameters:
    affine (napari.utils.transforms.Affine): The Affine transform object.

    Returns:
    str: A single-line string representation of the affine transform.
    """
    if not isinstance(affine, Affine):
        return "Invalid affine transform object"

    # Function to format numpy arrays to string
    # Extracting properties of the affine transformation
    affine_matrix_str = array_to_single_line_string(affine.affine_matrix)

    return affine_matrix_str


def array_to_single_line_string(array):
    """
    Return a single-line string representation of a NumPy array with elements separated by commas.
    
    Parameters:
        array (numpy.ndarray): The array to be converted.
    
    Returns:
        str: The array formatted as a single line, with small values suppressed and no line breaks.
    """
    the_string = numpy.array2string(
        array,
        threshold=numpy.inf,
        separator=", ",
        max_line_width=numpy.inf,
        suppress_small=True,
    )
    the_string = the_string.replace("\n", "")
    return the_string


#
