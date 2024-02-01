from napari_chatgpt.utils.strings.markdown import extract_markdown_blocks

markdown_1 = """
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




markdown_2 = \
"""
To create a widget that inverts the colors of an image, we will follow these steps:
1. Define a function that accepts an image array as input. This image array can be 2D grayscale, 3D grayscale, or nD where the last dimension is assumed to be color channels (e.g., RGB).
2. Inside the function, convert the image array to float type for processing.
3. Invert the colors of the image by subtracting the image data from the maximum possible value. For an image with values ranging from 0 to 1, this would be `1 - image_data`. For an image with values ranging from 0 to 255, it would be `255 - image_data`.
4. Decorate the function with the `@magicgui` decorator, specifying the call button text and setting `result_widget=False` since the function will return an image array.
5. Return the inverted image array.
Now, let's write the corresponding code:
```python
from napari.types import ImageData
from magicgui import magicgui
import numpy as np
@magicgui(call_button='Invert Colors', result_widget=False)
def invert_colors(image: ImageData) -> ImageData:
    # Convert the image to float for processing
    image_float = image.astype(float)
    
    # Invert the image colors
    inverted_image = 255.0 - image_float
    
    return inverted_image
# The function `invert_colors` can now be used as a widget in napari.
# When an image layer is selected, this widget will invert its colors.
```
This code defines a widget function that inverts the colors of an image. The function is decorated with `@magicgui` to create a GUI element in napari. When the user presses the "Invert Colors" button, the selected image's colors will be inverted, and the result will be displayed in the napari viewer.
"""

def test_extract_markdown_blocks_1():
    blocks = extract_markdown_blocks(markdown_1)

    print(blocks[0])
    print(blocks[1])
    print(blocks[2])

    assert len(blocks) == 3
    assert '```' not in blocks[0]
    assert '```' in blocks[1]
    assert '```' not in blocks[2]

def test_extract_markdown_blocks_2():
    blocks = extract_markdown_blocks(markdown_2)

    print(blocks[0])
    print(blocks[1])
    print(blocks[2])

    assert len(blocks) == 3
    assert '```' not in blocks[0]
    assert '```' in blocks[1]
    assert '```' not in blocks[2]