from typing import Optional

from napari.types import ArrayLike
from numpy import ndarray

from napari_chatgpt.omega.tools.napari.delegated_code.classic import \
    classic_segmentation


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

    # Falling back to classic segmentation if image is 3D or more:
    if len(image.shape) > 2:
        return classic_segmentation(image,
                                     normalize=normalize,
                                     norm_range_low=norm_range_low,
                                     norm_range_high=norm_range_high)

    # Convert image to float
    image = image.astype(float, copy=False)

    # Load appropriate StarDist models:
    if len(image.shape) == 2:
        from stardist.models import StarDist2D
        model = StarDist2D.from_pretrained(model_type)
    else:
        raise ValueError("Image should be 2D.")

    # If normalize is True, normalize the image:
    if normalize:
        from napari_chatgpt.utils.images.normalize import normalize_img
        image = normalize_img(image, norm_range_low, norm_range_high)

    # Run StarDist:
    labels, _ = model.predict_instances(image, scale=scale)

    return labels


