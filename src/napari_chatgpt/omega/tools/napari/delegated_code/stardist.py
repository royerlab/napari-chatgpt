from typing import Optional, Any

import numpy
from napari.types import ArrayLike
from numpy import ndarray

from napari_chatgpt.utils.segmentation.labels_3d_merging import \
    merge_2d_segments


### SIGNATURE
def stardist_segmentation(image: ArrayLike,
                          model_type: str = '2D_versatile_fluo',
                          normalize: Optional[bool] = True,
                          norm_range_low: Optional[float] = 1.0,
                          norm_range_high: Optional[float] = 99.8,
                          min_segment_size: int = 32,
                          scale:float = None) -> ndarray:
    """
    StarDist cell segmentation function.

    Parameters
    ----------

    image: ArrayLike
            Image for which to segment cells. Must be 2D.

    model_type: str
            Model type, pre-trained models include: '2D_versatile_fluo', '2D_versatile_he'.
            '2D_versatile_fluo' is trained on a broad range of fluorescent 2D semantic
            segmentation images.
            '2D_versatile_he' is trained on H&E stained tissue (but may generalize to other
            staining modalities).


    normalize: Optional[bool]
            If True, normalizes the image to a given percentile range.
            If False, assumes that the image is already normalized to [0,1].

    norm_range_low: Optional[float]
            Lower percentile for normalization

    norm_range_high: Optional[float]
            Higher percentile for normalization

    min_segment_size: Optional[int]
            Minimum number of pixels in a segment. Segments smaller than this are removed.

    scale: Optional[float]
            Scaling factor that gets applied to the input image before prediction.
            This is useful if the input image has a different resolution than the model was trained on.

    Returns
    -------
    Segmented image as a labels array that can be added to napari as a Labels layer.

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

    # Load appropriate StarDist models:
    if len(image.shape) == 2:
        labels = stardist_2d(image,
                             scale=scale,
                             model_type=model_type)
    elif len(image.shape) == 3:
        labels = stardist_3d(image,
                             scale=scale,
                             model_type=model_type,
                             min_segment_size=min_segment_size)
    else:
        raise ValueError("Image must be 2D or 3D.")

    labels = remove_small_segments(labels, min_segment_size)

    return labels


def stardist_2d(image,
                scale: float,
                model_type: str,
                model: Optional[Any] = None):

    if model is None:
        # Get the StarDist model:
        from stardist.models import StarDist2D
        model = StarDist2D.from_pretrained(model_type)

    # Run StarDist:
    labels, _ = model.predict_instances(image, scale=scale)

    return labels

def stardist_3d(image,
                scale: float,
                model_type: str,
                min_segment_size: int):

    # Get the StarDist model once:
    from stardist.models import StarDist2D
    model = StarDist2D.from_pretrained(model_type)

    # Initialize an empty list to collect the segmented slices
    segmented_slices = []

    # Iterate over each slice of the 3D image
    for i in range(image.shape[0]):
        # Segment the current slice with stardist_segmentation
        # Note: We are not setting optional parameters as instructed
        segmented_slice = stardist_2d(image[i],
                                      scale=scale,
                                      model_type=model_type,
                                      model=model)

        segmented_slice = remove_small_segments(segmented_slice, min_segment_size=min_segment_size)

        # Append the segmented slice to the list
        segmented_slices.append(segmented_slice)

    # Stack the segmented slices to form a 3D segmented image
    segmented_image = numpy.stack(segmented_slices, axis=0)

    # Convert the segmented image to uint32 as required
    segmented_image = segmented_image.astype(numpy.uint32)

    # Merge overlapping segments:
    segmented_image = merge_2d_segments(segmented_image, overlap_threshold=1)

    return segmented_image

def remove_small_segments(labels, min_segment_size):
    # remove small segments:
    if min_segment_size > 0:
        from skimage.morphology import remove_small_objects
        labels = remove_small_objects(labels, min_segment_size)
    return labels
