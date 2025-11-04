from typing import Optional, Any

from napari.types import ArrayLike
from numpy import ndarray

from napari_chatgpt.utils.segmentation.labels_3d_merging import (
    segment_3d_from_segment_2d,
)


### SIGNATURE
def stardist_segmentation(
    image: ArrayLike,
    model_type: str = "versatile_fluo",
    normalize: Optional[bool] = True,
    norm_range_low: Optional[float] = 1.0,
    norm_range_high: Optional[float] = 99.8,
    min_segment_size: int = 32,
    scale: float = None,
) -> ndarray:
    """
    Segments cells in a 2D or 3D image using a StarDist model and returns a labeled mask.
    
    Parameters:
        image (ArrayLike): Input image to segment; must be 2D or 3D.
        model_type (str, optional): Name of the pretrained StarDist model to use. Common options include 'versatile_fluo' and 'versatile_he'.
        normalize (bool, optional): Whether to normalize the image intensity based on percentiles before segmentation.
        norm_range_low (float, optional): Lower percentile for normalization if enabled.
        norm_range_high (float, optional): Upper percentile for normalization if enabled.
        min_segment_size (int, optional): Minimum size (in pixels) for segments to retain; smaller segments are removed.
        scale (float, optional): Scaling factor to adjust image resolution before prediction.
    
    Returns:
        ndarray: Labeled segmentation mask suitable for use as a napari Labels layer.
    
    Raises:
        ValueError: If the input image is not 2D or 3D.
    """
    ### SIGNATURE

    # Raise an error if the image is not 2D or 3D:
    if len(image.shape) > 3:
        raise ValueError("The input image must be 2D or 3D.")

    # Add '2D_' as prefix to the model if not yet a prefix:
    if not model_type.startswith("2D_"):
        model_type = "2D_" + model_type

    # Convert image to float
    image = image.astype(float, copy=False)

    # If normalize is True, normalize the image:
    if normalize:
        from napari_chatgpt.utils.images.normalize import normalize_img

        image = normalize_img(image, norm_range_low, norm_range_high)

    # Load appropriate StarDist models:
    if len(image.shape) == 2:
        labels = stardist_2d(image, scale=scale, model_type=model_type)
    elif len(image.shape) == 3:
        labels = stardist_3d(
            image, scale=scale, model_type=model_type, min_segment_size=min_segment_size
        )
    else:
        raise ValueError("Image must be 2D or 3D.")

    labels = remove_small_segments(labels, min_segment_size)

    return labels


def stardist_2d(image, scale: float, model_type: str, model: Optional[Any] = None):
    """
    Segment a 2D image using a StarDist2D model and return the labeled mask.
    
    Parameters:
        image: The 2D image to segment.
        scale (float): Optional scaling factor for the image.
        model_type (str): Name of the pretrained StarDist2D model to use.
        model (Any, optional): An existing StarDist2D model instance. If not provided, the specified pretrained model is loaded.
    
    Returns:
        labels (ndarray): Labeled segmentation mask of the input image.
    """
    if model is None:
        # Get the StarDist model:
        from stardist.models import StarDist2D

        model = StarDist2D.from_pretrained(model_type)

    # Run StarDist:
    labels, _ = model.predict_instances(image, scale=scale)

    return labels


def stardist_3d(image, scale: float, model_type: str, min_segment_size: int):
    # Get the StarDist model once:
    """
    Performs 3D cell segmentation by applying a StarDist2D model to each 2D slice and merging the results.
    
    Parameters:
        image: The 3D image array to segment.
        scale (float): Scaling factor for the input image.
        model_type (str): Name of the pretrained StarDist2D model to use.
        min_segment_size (int): Minimum size (in pixels) for segmented objects to retain.
    
    Returns:
        ndarray: A 3D labeled array with unique integer labels for each segmented object.
    """
    from stardist.models import StarDist2D

    model = StarDist2D.from_pretrained(model_type)

    # Define a function to segment 2D slices:
    def segment_2d(image):
        """
        Segments a 2D image using a StarDist2D model.
        
        Returns:
            ndarray: Labeled segmentation mask of the input 2D image.
        """
        return stardist_2d(image, scale=scale, model_type=model_type, model=model)

    segmented_image = segment_3d_from_segment_2d(
        image, segment_2d_func=segment_2d, min_segment_size=min_segment_size
    )

    return segmented_image


def remove_small_segments(labels, min_segment_size):
    # remove small segments:
    """
    Remove connected components smaller than a specified size from a labeled segmentation mask.
    
    Parameters:
        labels (ndarray): Labeled array where each integer represents a segmented object.
        min_segment_size (int): Minimum size (in pixels or voxels) for segments to be retained.
    
    Returns:
        ndarray: Labeled array with small segments removed.
    """
    if min_segment_size > 0:
        from skimage.morphology import remove_small_objects

        labels = remove_small_objects(labels, min_segment_size)
    return labels
