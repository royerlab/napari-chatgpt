import napari
import pytest
from skimage import data
from skimage.segmentation import slic

from napari_chatgpt.utils.api_keys.api_key import is_api_key_available
from napari_chatgpt.utils.python.fix_code_given_error import \
    fix_code_given_error_message

_code_snippet_1 = \
"""
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

_error_1 = \
"""
```
Error Message: channel_axis=-1 indicates multichannel, which is not supported for a two-dimensional image; use channel_axis=None if the image is grayscale (ValueError)
```
"""

# @pytest.mark.skipif(not is_api_key_available('OpenAI'),
#                     reason="requires OpenAI key to run")
def _test_fix_code_given_error_1():

    # Instantiating Napari viewer headlessly:
    viewer = napari.Viewer(show=False)

    # IMAGE LAYER:
    cells = data.cells3d()[30, 1]  # grab some data
    viewer.add_image(cells, name='cells', colormap='magma')
    cells = data.coins()  # grab some data
    viewer.add_image(cells, name='coins', colormap='viridis')
    cells = data.astronaut()  # grab some data
    viewer.add_image(cells, name='astronaut')

    fixed_code = fix_code_given_error_message(_code_snippet_1, _error_1)
    print(fixed_code)

    assert ', channel_axis=None)' in fixed_code
