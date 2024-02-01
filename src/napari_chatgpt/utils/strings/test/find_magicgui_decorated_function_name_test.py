from napari_chatgpt.utils.strings.find_function_name import find_function_name, \
    find_magicgui_decorated_function_name

__some_register = {}

_some_code = """
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


def test_find_magicgui_decorated_function_name():
    function_name = find_magicgui_decorated_function_name(_some_code)

    assert function_name == 'generate_pattern_widget'
