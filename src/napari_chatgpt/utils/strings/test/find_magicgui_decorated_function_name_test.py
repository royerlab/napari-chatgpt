from napari_chatgpt.utils.strings.find_function_name import \
    find_magicgui_decorated_function_name


_some_code_1 = """
import numpy as np
from napari.types import ImageData
from magicgui import magicgui

# Define the function to create different patterns
def create_pattern(pattern_type: str, size: int = 1024) -> np.ndarray:
    image = np.zeros((size, size, 3), dtype=np.uint8)
    
    if pattern_type == 'Horizontal Gradient':
        for i in range(size):
            image[:, i] = i * 255 // size
    elif pattern_type == 'Vertical Gradient':
        for i in range(size):
            image[i, :] = i * 255 // size
    elif pattern_type == 'Diagonal Gradient':
        for i in range(size):
            image[i, i] = i * 255 // size
    elif pattern_type == 'Sine Wave Horizontal':
        for i in range(size):
            image[:, i] = (np.sin(i / size * 2 * np.pi) * 127.5 + 127.5).astype(np.uint8)
    elif pattern_type == 'Sine Wave Vertical':
        for i in range(size):
            image[i, :] = (np.sin(i / size * 2 * np.pi) * 127.5 + 127.5).astype(np.uint8)
    elif pattern_type == 'Checkerboard':
        checker_size = size // 8
        for i in range(0, size, checker_size):
            for j in range(0, size, checker_size):
                if (i // checker_size) % 2 == (j // checker_size) % 2:
                    image[i:i+checker_size, j:j+checker_size] = 255
    elif pattern_type == 'Circles':
        for i in range(size):
            for j in range(size):
                if ((i - size // 2) ** 2 + (j - size // 2) ** 2) ** 0.5 < size // 4:
                    image[i, j] = 255
    elif pattern_type == 'Spiral':
        x, y = np.ogrid[:size, :size]
        r = np.hypot(x - size / 2, y - size / 2)
        theta = np.arctan2(x - size / 2, y - size / 2)
        image[..., 0] = (np.sin(5 * theta + r / 10) * 127.5 + 127.5).astype(np.uint8)
    elif pattern_type == 'Random Noise':
        image = np.random.randint(0, 256, (size, size, 3), dtype=np.uint8)
    elif pattern_type == 'Stripes':
        stripe_width = size // 10
        for i in range(0, size, stripe_width):
            image[:, i:i+stripe_width] = (i // stripe_width) * 255 // (size // stripe_width)
    
    return image

# Define the widget function with the magicgui decorator
@magicgui(pattern_type={"choices": [
    'Horizontal Gradient', 'Vertical Gradient', 'Diagonal Gradient',
    'Sine Wave Horizontal', 'Sine Wave Vertical', 'Checkerboard',
    'Circles', 'Spiral', 'Random Noise', 'Stripes'
]}, call_button='Generate Pattern')
def generate_pattern_widget(pattern_type: str) -> ImageData:
    return create_pattern(pattern_type)

# The function can now be used as a widget in napari
# Example usage (assuming a napari viewer instance is available as `viewer`):
# viewer.window.add_dock_widget(generate_pattern_widget)
"""

_some_code_2 = """

# Note: code was modified to add missing imports:
from magicgui import magicgui
from napari.layers import Image, Labels, Points, Shapes, Surface, Tracks, Vectors
from napari.types import ImageData
from napari.types import ImageData, LabelsData, PointsData, ShapesData, SurfaceData, TracksData, VectorsData
from typing import Union
import numpy as np
import pywt
@magicgui(
    call_button="Fuse Images",
    wavelet_type={"choices": pywt.wavelist(kind='discrete')},
    decomposition_level={"widget_type": "Slider", 'min': 1, 'max': 10},
    combine_method={"choices": ['average', 'maximum']})
def wavelet_image_fusion(
    image1: ImageData, 
    image2: ImageData, 
    wavelet_type: str = 'haar', 
    decomposition_level: int = 1, 
    combine_method: str = 'average'
) -> ImageData:
    # Check if the images have the same shape
    if image1.shape != image2.shape:
        return f"Error: Images must have the same dimensions."
    # Perform wavelet decomposition on both images
    coeffs1 = pywt.wavedec2(image1, wavelet_type, level=decomposition_level)
    coeffs2 = pywt.wavedec2(image2, wavelet_type, level=decomposition_level)
    # Function to combine coefficients
    def combine_coeffs(c1, c2, method):
        if method == 'average':
            return (np.array(c1) + np.array(c2)) / 2
        elif method == 'maximum':
            return np.maximum(c1, c2)
    # Combine the coefficients
    fused_coeffs = []
    for c1, c2 in zip(coeffs1, coeffs2):
        if isinstance(c1, tuple):
            fused_coeffs.append(tuple(combine_coeffs(subc1, subc2, combine_method) for subc1, subc2 in zip(c1, c2)))
        else:
            fused_coeffs.append(combine_coeffs(c1, c2, combine_method))
    # Reconstruct the image from the combined coefficients
    fused_image = pywt.waverec2(fused_coeffs, wavelet_type)
    # Crop the image to the original size
    fused_image = fused_image[:image1.shape[0], :image1.shape[1]]
    return fused_image.astype(np.float32)
# Example usage:
# fused_image = wavelet_image_fusion(image1, image2, 'haar', 1, 'average')
"""
def test_find_magicgui_decorated_function_name():
    function_name = find_magicgui_decorated_function_name(_some_code_1)

    assert function_name == 'generate_pattern_widget'

    function_name = find_magicgui_decorated_function_name(_some_code_2)

    assert function_name == 'wavelet_image_fusion'
