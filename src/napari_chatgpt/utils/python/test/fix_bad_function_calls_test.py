import pytest
from arbol import aprint

from napari_chatgpt.utils.api_keys.api_key import is_api_key_available
from napari_chatgpt.utils.python.fix_bad_fun_calls import fix_all_bad_function_calls

_code_snippet_1 = \
"""
import numpy as np

data = pd.read_csv("data.csv")
result = np.mean(data["value"])
"""

_code_snippet_2 = \
"""
from magicgui import magicgui
from napari.types import ImageData, LabelsData, PointsData, ShapesData, SurfaceData, TracksData, VectorsData
import numpy as np
from typing import Union
from napari.types import ImageData
from napari.layers import Image
from magicgui import magicgui
import numpy as np

@magicgui(call_button='Run')
def structure_tensor_trace(viewer: 'napari.viewer.Viewer', layer: Image) -> ImageData:
    data = np.copy(layer.data)
    data = data.astype(float)
    
    kernel_size = 3
    kernel = np.ones((kernel_size,kernel_size))
    Ix = scipy.signal.convolve2d(data, kernel, mode='same', boundary='symm')
    Iy = scipy.signal.convolve2d(data, kernel.T, mode='same', boundary='symm')
    
    Ixx = Ix*Ix 
    Iyy = Iy*Iy
    Ixy = Ix*Iy
    
    trace = Ixx + Iyy 
    return trace
"""

_code_snippet_3 = \
"""
import numpy as np
from skimage import feature, transform
from napari.types import ImageData, LabelsData
from magicgui import magicgui

@magicgui(call_button='Find Straight Lines')
def find_straight_lines(image: ImageData) -> LabelsData:
    edges = feature.canny(image)
    hough_lines = transform.probabilistic_hough_line(edges)

    labels = np.zeros_like(image, dtype=np.uint32)
    label_counter = 1

    for line in hough_lines:
        (x1, y1), (x2, y2) = line
        rr, cc = np.array(transform.line(x1, y1, x2, y2))
        labels[rr, cc] = label_counter
        label_counter += 1

    return labels
"""


@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_fix_bad_call_1():
    fixed_code, did_something = fix_all_bad_function_calls(_code_snippet_1)
    aprint(fixed_code)

    assert not did_something


@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_fix_bad_call_2():
    fixed_code, did_something  = fix_all_bad_function_calls(_code_snippet_2)
    aprint(fixed_code)

    assert not did_something

@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_fix_bad_call_3():
    fixed_code, did_something  = fix_all_bad_function_calls(_code_snippet_3)
    aprint(fixed_code)

    assert did_something
    assert 'skimage.draw.line' in fixed_code
