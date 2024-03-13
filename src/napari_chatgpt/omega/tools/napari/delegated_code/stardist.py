from typing import Optional, Any

from napari.types import ArrayLike
from numpy import ndarray

from napari_chatgpt.utils.segmentation.labels_3d_merging import \
    segment_3d_from_segment_2d


### SIGNATURE
def stardist_segmentation(image: ArrayLike,
                          model_type: str = 'versatile_fluo',
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
            Image for which to segment cells. Must be 2D or 3D.

    model_type: str
            Model type, pre-trained models include: 'versatile_fluo', 'versatile_he'.
            'versatile_fluo' is trained on a broad range of fluorescent images.
            'versatile_he' is trained on H&E stained tissue (but may generalize to other
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

    # Add '2D_' as prefix to the model if not yet a prefix:
    if not model_type.startswith('2D_'):
        model_type = '2D_' + model_type

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

    # Define a function to segment 2D slices:
    def segment_2d(image):
        return stardist_2d(image,
                             scale=scale,
                             model_type=model_type,
                             model=model)

    segmented_image = segment_3d_from_segment_2d(image,
                                                 segment_2d_func=segment_2d,
                                                 min_segment_size=min_segment_size)

    return segmented_image

def remove_small_segments(labels, min_segment_size):
    # remove small segments:
    if min_segment_size > 0:
        from skimage.morphology import remove_small_objects
        labels = remove_small_objects(labels, min_segment_size)
    return labels
