import numpy as np
from napari.types import ArrayLike
from numpy import ravel, percentile


def normalize_img(image: ArrayLike,
                  p_low: float,
                  p_high: float,
                  clip: bool = True) -> ArrayLike:
    """
    Normalize the image to a given percentile range.

    Parameters
    ----------
    image: ArrayLike
        The image to be normalized

    p_low: float
        The lower percentile to normalize the image

    p_high: float
        The higher percentile to normalize the image

    clip: bool
        If True, clip the normalized image between 0 and 1

    Returns
    -------
    Normalized image
    """
    # Calculate lower and higher percentiles:
    v_low, v_high = percentile(ravel(image), [p_low, p_high])

    # rescale the image:
    normalized_image = (image - v_low) / (v_high - v_low + 1e-6)

    # Clip between 0 and 1:
    if clip:
        normalized_image = np.clip(normalized_image, 0, 1)

    return normalized_image
