import pytest
from arbol import aprint

from napari_chatgpt.utils.api_keys.api_key import is_api_key_available
from napari_chatgpt.utils.python.required_imports import required_imports

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


@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_required_imports_1():
    imports = required_imports(_code_snippet_1)
    aprint(imports)

    assert 'import numpy as np' in imports
    assert 'import pandas as pd' in imports


@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_required_imports_2():
    imports = required_imports(_code_snippet_2)
    aprint(imports)

    assert 'import scipy.signal' in imports
