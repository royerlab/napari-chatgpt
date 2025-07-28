import pytest

from napari_chatgpt.llm.litemind_api import is_llm_available
from napari_chatgpt.utils.python.missing_packages import required_packages

___generated_python_code = """
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


@pytest.mark.skipif(not is_llm_available(), reason="requires LLM to run")
def test_missing_packages():
    packages = required_packages(___generated_python_code)
    print(packages)
    assert packages
    assert (
        "PyQt5" in packages
        or "napari" in packages
        or any("opencv-python" in p for p in packages)
    )
