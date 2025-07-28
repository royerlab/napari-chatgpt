from typing import Optional

from napari.types import ArrayLike
from numpy import zeros, uint32, ndarray
from scipy.ndimage import label, distance_transform_edt, gaussian_filter
from skimage.feature import peak_local_max
from skimage.filters import (
    threshold_otsu,
    threshold_yen,
    threshold_li,
    threshold_minimum,
    threshold_triangle,
    threshold_mean,
    threshold_isodata,
)
from skimage.measure import label
from skimage.morphology import (
    closing,
    disk,
    ball,
    remove_small_objects,
    erosion,
    opening,
)
from skimage.segmentation import watershed


### SIGNATURE
def classic_segmentation(
    image: ArrayLike,
    threshold_type: str = "otsu",
    normalize: Optional[bool] = True,
    norm_range_low: Optional[float] = 1.0,
    norm_range_high: Optional[float] = 99.8,
    min_segment_size: int = 32,
    erosion_steps: int = 1,
    closing_steps: int = 1,
    opening_steps: int = 0,
    apply_watershed: bool = False,
    min_distance: int = 15,
) -> ndarray:
    """
    Segments cells in a 2D or 3D image using thresholding, morphological operations, and optional watershed segmentation.
    
    Parameters:
        image (ArrayLike): Input image to segment; must be 2D or 3D.
        threshold_type (str): Thresholding algorithm to use. Supported values: 'otsu', 'yen', 'li', 'minimum', 'triangle', 'mean', 'isodata'.
        normalize (Optional[bool]): If True, normalizes image intensity to the specified percentile range before processing.
        norm_range_low (Optional[float]): Lower percentile for normalization.
        norm_range_high (Optional[float]): Upper percentile for normalization.
        min_segment_size (int): Minimum size (in pixels) for segments to keep; smaller segments are removed.
        erosion_steps (int): Number of erosion operations to apply before thresholding.
        closing_steps (int): Number of closing operations to apply after thresholding.
        opening_steps (int): Number of opening operations to apply after thresholding.
        apply_watershed (bool): If True, applies watershed segmentation on the distance transform of the binary image.
        min_distance (int): Minimum distance between peaks for watershed segmentation.
    
    Returns:
        ndarray: Labeled segmentation image as a uint32 NumPy array, suitable for use as a labels layer in napari.
    
    Raises:
        ValueError: If an unsupported threshold_type is provided.
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
        "otsu": threshold_otsu,
        "yen": threshold_yen,
        "li": threshold_li,
        "minimum": threshold_minimum,
        "triangle": threshold_triangle,
        "mean": threshold_mean,
        "isodata": threshold_isodata,
    }.get(threshold_type)

    if threshold_func is None:
        raise ValueError(
            "threshold_type must be one of: 'otsu', 'yen', 'li', 'minimum', 'triangle', 'mean', 'isodata'."
        )

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
        coords = peak_local_max(
            distance, min_distance=min_distance, labels=binary_image
        )

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
