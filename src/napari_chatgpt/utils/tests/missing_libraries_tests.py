import pytest

from napari_chatgpt.utils.missing_libraries import required_libraries, \
    pip_install
from napari_chatgpt.utils.openai_key import is_openai_key_available

generated_python_code = """

from magicgui import magicgui
from napari.types import ImageData, LabelsData, PointsData, ShapesData, SurfaceData, TracksData, VectorsData
import numpy as np
from typing import Union
from napari.types import ImageData
from magicgui import magicgui
import numpy as np
import cv2

@magicgui(call_button='Run')
def denoise_bilateral(image: ImageData, d: int = 15, sigmaColor: float = 75, sigmaSpace: float = 75) -> ImageData:
    img = image.astype(np.float32)
    img = cv2.bilateralFilter(img, d, sigmaColor, sigmaSpace)
    return img

"""

@pytest.mark.skipif(not is_openai_key_available(), reason="requires OpenAI key to run")
def test_pip_install_missing():
    libraries = required_libraries(generated_python_code)
    print(libraries)
    assert libraries

    pip_install(libraries)
