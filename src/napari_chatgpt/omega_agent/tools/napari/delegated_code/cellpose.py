from typing import Sequence, Optional

from napari.types import ArrayLike
from numpy import ndarray


### SIGNATURE
def cellpose_segmentation(
    image: ArrayLike,
    model_type: str = "cyto",
    normalize: Optional[bool] = True,
    norm_range_low: Optional[float] = 1.0,
    norm_range_high: Optional[float] = 99.8,
    min_segment_size: int = 32,
    channel: Optional[Sequence[int]] = None,
    diameter: Optional[float] = None,
) -> ndarray:
    """
    Performs cell segmentation on 2D or 3D images using the Cellpose deep learning model.
    
    The function supports optional intensity normalization, configurable model types, channel selection, and removal of small segmented objects. Returns a labeled array suitable for visualization or further analysis.
    
    Parameters:
        image (ArrayLike): Input image to segment; must be 2D or 3D.
        model_type (str): Cellpose model type ('cyto', 'nuclei', or 'cyto2').
        normalize (Optional[bool]): If True, normalizes image intensity to the specified percentile range.
        norm_range_low (Optional[float]): Lower percentile for normalization.
        norm_range_high (Optional[float]): Upper percentile for normalization.
        min_segment_size (int): Minimum pixel size for segments; smaller segments are removed.
        channel (Optional[Sequence[int]]): Channel specification for segmentation and optional nuclear channel; defaults to [0, 0].
        diameter (Optional[float]): Estimated cell diameter; if None, estimated per image or set to 30 for 3D images.
    
    Returns:
        ndarray: Labeled array of segmented cells.
    """
    ### SIGNATURE

    # Raise an error if the image is not 2D or 3D:
    if len(image.shape) > 3:
        raise ValueError("The input image must be 2D or 3D.")

    # Convert image to float
    image = image.astype(float, copy=False)

    # If normalize is True, normalize the image:
    if normalize:
        from napari_chatgpt.utils.images.normalize import normalize_img

        image = normalize_img(image, norm_range_low, norm_range_high)

    if channel is None:
        channel = [0, 0]

    # Load cellpose models:
    from cellpose import models

    model = models.Cellpose(model_type=model_type)

    if len(image.shape) == 2:
        # Run cellpose in 2D mode:
        labels, _, _, _ = model.eval([image], diameter=diameter, channels=[channel])
    elif len(image.shape) == 3:

        # If no diameter is provided, use a default value:
        if diameter is None:
            diameter = 30.0

        # Run cellpose in 3D mode:
        labels, _, _, _ = model.eval(
            [image], diameter=diameter, channels=[channel], do_3D=True, z_axis=0
        )
    # Get the first label array from the list:
    labels = labels[0]

    # Remove small segments:
    labels = remove_small_segments(labels, min_segment_size)

    return labels


def remove_small_segments(labels, min_segment_size):
    # remove small segments:
    """
    Remove segments smaller than a specified size from a labeled image.
    
    Parameters:
        labels: An array of labeled regions.
        min_segment_size: Minimum number of pixels a segment must have to be retained.
    
    Returns:
        The label image with segments smaller than the specified size removed.
    """
    if min_segment_size > 0:
        from skimage.morphology import remove_small_objects

        labels = remove_small_objects(labels, min_segment_size)
    return labels
