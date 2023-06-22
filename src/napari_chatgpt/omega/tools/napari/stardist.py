from typing import Optional

from napari.types import ArrayLike


### SIGNATURE
def stardist_segmentation(image: ArrayLike,
                          model_type: str = '2D_versatile_fluo',
                          normalize: Optional[bool] = True,
                          norm_range_low: Optional[float] = 1.0,
                          norm_range_high: Optional[float] = 99.8,
                          scale:float = None) -> ArrayLike:
    """
    StarDist cell segmentation function.

    Parameters
    ----------

    image: ArrayLike
            Image for which to segment cells. Can be 2D or 3D.

    model_type: str
            Model type, pre-trained models include: '2D_versatile_fluo', '2D_versatile_he', '3D_versatile_fluo'.
            '2D_versatile_fluo' is trained on a broad range of fluorescent 2D semantic
            segmentation images.
            '2D_versatile_he' is trained on H&E stained tissue (but may generalize to other
            staining modalities).
            '3D_versatile_fluo' is trained for 3D fluorescence microscopy images.

    normalize: Optional[bool]
            If True, normalizes the image to a given percentile range.
            If False, assumes that the image is already normalized to [0,1].

    norm_range_low: Optional[float]
            Lower percentile for normalization

    norm_range_high: Optional[float]
            Higher percentile for normalization

    scale: Optional[float]
            Scaling factor that gets applied to the input image before prediction.
            This is useful if the input image has a different resolution than the model was trained on.

    Returns
    -------
    Segmented image as a labels array that can be added to napari as a Labels layer.

    """
    if len(image.shape) not in [2, 3]:
        raise ValueError("Image should be 2D or 3D.")

    # Correct model_type if necessary:
    if len(image.shape) == 3 and model_type == '2D_versatile_fluo':
        model_type = '3D_versatile_fluo'
    if len(image.shape) == 2 and model_type == '3D_versatile_fluo':
        model_type = '2D_versatile_fluo'

    # Load appropriate StarDist models:
    if len(image.shape) == 2:
        from stardist.models import StarDist2D
        model = StarDist2D.from_pretrained(model_type)
    elif len(image.shape) == 3:
        from stardist.models import StarDist3D
        model = StarDist3D.from_pretrained(model_type)
    else:
        raise ValueError("Image should be 2D or 3D.")

    # If normalize is True, normalize the image:
    if normalize:
        from napari_chatgpt.utils.images.normalize import normalize_img
        image = normalize_img(image, norm_range_low, norm_range_high)

    # Run StarDist:
    labels, _ = model.predict_instances(image, scale=scale)

    return labels


