from typing import Optional

from napari.types import ArrayLike
from numpy import zeros, uint32, ndarray
from scipy.ndimage import label, distance_transform_edt, gaussian_filter
from skimage.feature import peak_local_max
from skimage.filters import (threshold_otsu, threshold_yen, threshold_li,
                             threshold_minimum, threshold_triangle,
                             threshold_mean, threshold_isodata)
from skimage.measure import label
from skimage.morphology import closing, disk, ball, remove_small_objects, \
    erosion, opening
from skimage.segmentation import watershed


### SIGNATURE
def classic_segmentation(image: ArrayLike,
                         threshold_type: str = 'otsu',
                         normalize: Optional[bool] = True,
                         norm_range_low: Optional[float] = 1.0,
                         norm_range_high: Optional[float] = 99.8,
                         min_segment_size: int = 32,
                         erosion_steps: int = 1,
                         closing_steps: int = 1,
                         opening_steps: int = 0,
                         apply_watershed: bool = False,
                         min_distance: int = 15) -> ndarray:
    """
    Classic cell segmentation function.

    Parameters
    ----------

    image: ArrayLike
            Image for which to segment cells. Can be 2D or 3D.

    threshold_type: str
            Algorithm to use for thresholding. Options include: 'otsu', 'yen', 'li', 'minimum', 'triangle', 'mean', 'isodata'.

    normalize: Optional[bool]
            If True, normalizes the image to a given percentile range.
            If False, assumes that the image is already normalized to [0,1].

    norm_range_low: Optional[float]
            Lower percentile for normalization

    norm_range_high: Optional[float]
            Higher percentile for normalization

    min_segment_size: Optional[int]
            Minimum number of pixels in a segment. Segments smaller than this are removed.

    erosion_steps: Optional[int]
            Number of iterations of the erosion operator to apply to the image.

    closing_steps: Optional[int]
            Number of iterations of the closing operator to apply to the thresholded image.

    opening_steps: Optional[int]
            Number of iterations of the opening operator to apply to the thresholded image.

    apply_watershed: Optional[bool]
            If True, applies the watershed algorithm to the distance transform of the thresholded image.

    min_distance: Optional[int]
            Minimum number of pixels separating peaks in a region of `2 * min_distance + 1`

    Returns
    -------
    Segmented image as a labels array that can be added to napari as a Labels layer.

    """

    # Convert image to float
    image = image.astype(float, copy=False)

    # # Remove background:
    # background_scale = 50
    # footprint = disk(background_scale) if len(image.shape) == 2 else ball(background_scale)
    # image = white_tophat(image, footprint=footprint)

    # If normalize is True, normalize the image:
    if normalize:
        from napari_chatgpt.utils.images.normalize import normalize_img
        image = normalize_img(image, norm_range_low, norm_range_high)

    # Get appropriate thresholding function
    threshold_func = {
        'otsu': threshold_otsu,
        'yen': threshold_yen,
        'li': threshold_li,
        'minimum': threshold_minimum,
        'triangle': threshold_triangle,
        'mean': threshold_mean,
        'isodata': threshold_isodata
    }.get(threshold_type)

    if threshold_func is None:
        raise ValueError(
            "threshold_type must be one of: 'otsu', 'yen', 'li', 'minimum', 'triangle', 'mean', 'isodata'.")

    # Erosion steps:
    footprint = disk(2) if len(image.shape) == 2 else ball(2)
    for _ in range(erosion_steps):
        image = erosion(image, footprint=footprint)

    # Compute threshold value:
    threshold_value = threshold_func(image)

    # Apply threshold:
    binary_image = image > threshold_value

    # Apply the closing  and opening operators a given number of steps:
    for _ in range(closing_steps):
        binary_image = closing(binary_image, footprint=footprint)
    for _ in range(opening_steps):
        binary_image = opening(binary_image, footprint=footprint)

    if apply_watershed:

        # Gaussian filtered binary image:
        sigma = min_distance / 3
        filtered_binary_image = gaussian_filter(binary_image.astype(float), sigma=sigma)

        # Compute new threshold value:
        threshold_value = threshold_func(filtered_binary_image)

        # Apply threshold:
        modified_binary_image = filtered_binary_image > threshold_value

        # Compute Euclidean distance from every binary pixel
        # to the nearest zero pixel and return the result
        distance = distance_transform_edt(modified_binary_image)

        # Find peaks in an image, and return them as coordinates or a boolean array
        coords = peak_local_max(distance, min_distance=min_distance, labels=binary_image)

        # Create a mask from the coordinates by dilating the peaks
        mask = zeros(distance.shape, dtype=bool)
        mask[tuple(coords.T)] = True
        markers = label(mask)

        # Perform watershed segmentation
        labels = watershed(-distance, markers, mask=binary_image)
    else:
        # Label the thresholded image:
        labels = label(binary_image)

    # Remove small objects:
    labels = remove_small_objects(labels, min_segment_size)

    # Convert the segmented image to np.uint32 before returning the segmentation
    labels = labels.astype(uint32)

    return labels




