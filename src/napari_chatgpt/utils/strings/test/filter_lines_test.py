from napari_chatgpt.utils.strings.filter_lines import filter_lines

___text = """
from magicgui import magicgui
from typing import Union
from napari.types import ImageData
from magicgui import magicgui
import numpy as np
from scipy.signal import convolve2d
from scipy.ndimage import gaussian_filter
@magicgui(call_button='Run')
def lucy_richardson_deconvolution(image: ImageData, sigma: float = 1.0, iterations: int = 10) -> Union[np.ndarray, None]:
    kernel_size = 32
    kernel = np.zeros((kernel_size, kernel_size))
    kernel[kernel_size//2, kernel_size//2] = 1
    kernel = gaussian_filter(kernel, sigma=sigma)
    kernel /= np.sum(kernel)
    img = image.copy()
    for i in range(iterations):
        blurred = convolve2d(img, kernel, mode='same')
        ratio = image / blurred
        img *= convolve2d(ratio, np.rot90(kernel, 2), mode='same')
    return img
viewer.window.add_dock_widget(lucy_richardson_deconvolution)
"""


def test_filter_lines():
    filtered_text = filter_lines(___text, ['viewer.window.add_dock_widget'])

    assert not 'viewer.window.add_dock_widget' in filtered_text
