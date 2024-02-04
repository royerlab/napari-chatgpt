from napari_chatgpt.utils.strings.trailing_code import remove_trailing_code

___code = \
'''
import numpy as np
from napari.types import ImageData
from napari.layers import Image
from magicgui import magicgui

@magicgui(call_button='Generate Image', width={"widget_type": "IntSlider", 'min': 1, 'max': 1000}, height={"widget_type": "IntSlider", 'min': 1, 'max': 1000}, mean={"widget_type": "FloatSlider", 'min': 0.0, 'max': 1.0}, sigma={"widget_type": "FloatSlider", 'min': 0.0, 'max': 1.0})
def generate_gaussian_noise_image(width: int, height: int, mean: float, sigma: float) -> ImageData:
    image = np.random.normal(mean, sigma, (height, width))
    return image

result = generate_gaussian_noise_image()
viewer.add_image(result)
'''


def test_trailing_code():

    result = remove_trailing_code(___code)

    print('')
    print(result)

    assert 'result = generate_gaussian_noise_image()' not in result
    assert 'viewer.add_image(result)' not in result
