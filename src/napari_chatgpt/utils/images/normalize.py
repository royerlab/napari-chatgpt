import numpy as np
from napari.types import ArrayLike
from scipy.ndimage import percentile_filter


def normalize_img(image: ArrayLike, p_low: float, p_high: float) -> ArrayLike:
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

    Returns
    -------
    Normalized image
    """
    # Calculate lower and higher percentiles:
    v_low, v_high = np.percentile(image, [p_low, p_high])

    # rescale the image:
    normalized_image = (image - v_low) / (v_high - v_low + 1e-6)

    return normalized_image
