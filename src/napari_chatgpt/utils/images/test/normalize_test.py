import numpy as np

from napari_chatgpt.utils.images.normalize import normalize_img


def test_normalize_img():
    # Step 1: Create a mock image
    image = np.arange(100).reshape(10, 10)

    # Step 2: Call the normalize_img function
    p_low, p_high = 5, 95
    normalized_image = normalize_img(image, p_low, p_high)

    # Step 3: Assert that the returned normalized image has its min and max values within the expected range
    assert np.isclose(normalized_image.min(), 0, atol=1e-6)
    assert np.isclose(normalized_image.max(), 1, atol=1e-6)
