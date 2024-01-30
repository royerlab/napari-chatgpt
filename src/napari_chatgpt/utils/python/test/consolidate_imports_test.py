from pprint import pprint

from napari_chatgpt.utils.python.consolidate_imports import consolidate_imports
from napari_chatgpt.utils.python.dynamic_import import dynamic_import, \
    execute_as_module


code_to_consolidate_imports = \
"""
import napari
import numpy as np
from scipy.ndimage import gaussian_filter




import napari
import numpy as np
from scipy.ndimage import gaussian_filter

# Step 1: Retrieve the selected image layer from the viewer.
selected_image_layer = viewer.layers.selection.active

# Step 2: Convert the image data to float type if it's not already.
image_data = np.asarray(selected_image_layer.data, dtype=float)

# Step 3: Apply a Gaussian filter with sigma=2 to the image data.
filtered_image_data = gaussian_filter(image_data, sigma=2)

# Step 4: Add the filtered image as a new layer to the viewer.
viewer.add_image(filtered_image_data, name=f"{selected_image_layer.name}_gaussian_filtered")

# Step 5: Print the result of the operation.
print("Applied a Gaussian filter with sigma=2 to the selected image.")
"""


def test_consolidate_imports():
    result = consolidate_imports(code_to_consolidate_imports)

    print('')
    print(result)

    assert len(result.split('\n')) == 20
