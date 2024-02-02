from napari_chatgpt.utils.notebook.jupyter_notebook import JupyterNotebookFile

markdown = """
### Agent:
Tool response:
```python
import numpy as np
from napari.types import ImageData, Image
from napari.layers import Image as ImageLayer
from skimage.color import rgb2hsv, rgb2lab, rgb2gray
from magicgui import magicgui
from napari import Viewer

@magicgui(
    color_space={"choices": ["HSV", "LAB", "Grayscale"]},
    hue={"widget_type": "FloatSlider", 'min': 0.0, 'max': 1.0},
    saturation={"widget_type": "FloatSlider", 'min': 0.0, 'max': 1.0},
    value={"widget_type": "FloatSlider", 'min': 0.0, 'max': 1.0},
    apply_conversion={"call_button": "Apply Conversion"},
    result_widget=True
)
def color_space_explorer(
    viewer: Viewer,
    color_space: str,
    hue: float = 0.5,
    saturation: float = 0.5,
    value: float = 0.5,
    apply_conversion: bool = False
) -> ImageData:
    
    selected_layer = viewer.layers.selection.active
    if not isinstance(selected_layer, ImageLayer):
        return "Please select an image layer."
    
    image_data = np.copy(selected_layer.data)
    if image_data.dtype != np.float32:
        image_data = image_data.astype(np.float32) / 255.0
    
    def convert_color_space(image, color_space, hue, saturation, value):
        if color_space == "HSV":
            hsv_image = rgb2hsv(image)
            hsv_image[..., 0] = hue
            hsv_image[..., 1] = saturation
            hsv_image[..., 2] = value
            return hsv_image
        elif color_space == "LAB":
            lab_image = rgb2lab(image)
            # LAB adjustments are not straightforward like HSV
            # Typically, users don't adjust LAB channels directly
            return lab_image
        elif color_space == "Grayscale":
            gray_image = rgb2gray(image)
            return gray_image[..., np.newaxis]
        else:
            return image
    
    preview_image = convert_color_space(image_data, color_space, hue, saturation, value)
    
    if apply_conversion:
        # Update the selected layer with the converted image
        selected_layer.data = preview_image
        return "Conversion applied."
    else:
        # Return the preview image without updating the layer
        return preview_image

# This function would be added to the napari viewer as a widget
# and is not meant to be called directly in a script.
# To add this widget to the napari viewer, you would use the following:
# viewer.window.add_dock_widget(color_space_explorer)
```

This widget function `color_space_explorer` allows the user to explore different color spaces and adjust parameters relevant to the selected color space. The user can select the target color space from a dropdown menu, adjust parameters using sliders, and apply the conversion to the selected image layer. The function also provides a preview of the converted image before applying it. The function is decorated with `magicgui` to create an interactive GUI within napari.
"""

def test_add_and_split_markdown():

    jnf = JupyterNotebookFile()
    jnf.add_markdown_cell(markdown)

    assert len(jnf.notebook.cells) == 3
    assert '```' not in jnf.notebook.cells[0].source
    assert '```' in jnf.notebook.cells[1].source
    assert '```' not in jnf.notebook.cells[2].source



