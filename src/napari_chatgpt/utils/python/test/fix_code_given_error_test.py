import pytest

from napari_chatgpt.llm.litemind_api import is_llm_available
from napari_chatgpt.utils.python.fix_code_given_error import (
    fix_code_given_error_message,
)

_code_snippet_1 = """
    ```python
    import numpy as np
    import skimage.segmentation as seg
    # Get the selected image layer
    selected_layer = viewer.layers.selection.active
    # Apply SLIC superpixel algorithm to the selected image
    slic_image = seg.slic(selected_layer.data.astype(float), n_segments=100, compactness=10)
    # Add the SLIC superpixel image as a new label layer
    viewer.add_labels(slic_image)
    # Print statement
    print("SLIC superpixel algorithm applied to the selected image and added as a new label layer.")
    ```
    """

_error_1 = """
    ```
    Error Message: channel_axis=-1 indicates multichannel, which is not supported for a two-dimensional image; use channel_axis=None if the image is grayscale (ValueError)
    ```
    """


@pytest.mark.skipif(not is_llm_available(), reason="requires LLM to run")
@pytest.mark.llm
def test_fix_code_given_error_1():
    fixed_code, was_fixed = fix_code_given_error_message(_code_snippet_1, _error_1)
    assert was_fixed
    assert "channel_axis" in fixed_code
