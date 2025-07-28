import numpy as np
from napari.types import ArrayLike
from numpy import ravel, percentile


def normalize_img(
    image: ArrayLike, p_low: float, p_high: float, clip: bool = True
) -> ArrayLike:
    """
    Normalize an image array based on specified lower and upper percentiles.
    
    The function rescales the input image so that the values at `p_low` and `p_high` percentiles map to 0 and 1, respectively. Optionally, the output can be clipped to the [0, 1] range.
    
    Parameters:
        image (ArrayLike): Input image array to normalize.
        p_low (float): Lower percentile for normalization.
        p_high (float): Upper percentile for normalization.
        clip (bool, optional): If True, clips the normalized image to [0, 1]. Defaults to True.
    
    Returns:
        ArrayLike: The normalized (and optionally clipped) image array.
    """
    # Calculate lower and higher percentiles:
    v_low, v_high = percentile(ravel(image), [p_low, p_high])

    # rescale the image:
    normalized_image = (image - v_low) / (v_high - v_low + 1e-6)

    # Clip between 0 and 1:
    if clip:
        normalized_image = np.clip(normalized_image, 0, 1)

    return normalized_image
