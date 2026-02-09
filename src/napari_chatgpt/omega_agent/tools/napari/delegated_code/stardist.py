from typing import Any

from napari.types import ArrayLike
from numpy import ndarray

from napari_chatgpt.utils.segmentation.labels_3d_merging import (
    segment_3d_from_segment_2d,
)
from napari_chatgpt.utils.segmentation.remove_small_segments import (
    remove_small_segments,
)


### SIGNATURE
def stardist_segmentation(
    image: ArrayLike,
    model_type: str = "versatile_fluo",
    normalize: bool | None = True,
    norm_range_low: float | None = 1.0,
    norm_range_high: float | None = 99.8,
    min_segment_size: int = 32,
    scale: float = None,
) -> ndarray:
    """
    StarDist cell segmentation function.

    Parameters
    ----------

    image: ArrayLike
            Image for which to segment cells. Must be 2D or 3D.

    model_type: str
            Model type, pre-trained models include: 'versatile_fluo', 'versatile_he',
            'paper_dsb2018', 'demo'.
            'versatile_fluo' is trained on a broad range of fluorescent images.
            'versatile_he' is trained on H&E stained tissue (but may generalize to other
            staining modalities).
            For 3D images, segmentation is done slice-by-slice using the 2D model.
            Do NOT use 3D model names — only the above 2D models are valid.


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

    # Valid StarDist2D pretrained model names (with and without '2D_' prefix):
    _valid_models = {
        "versatile_fluo",
        "versatile_he",
        "paper_dsb2018",
        "demo",
        "2D_versatile_fluo",
        "2D_versatile_he",
        "2D_paper_dsb2018",
        "2D_demo",
    }

    # Validate model_type:
    if model_type not in _valid_models:
        raise ValueError(
            f"Unknown StarDist model_type: '{model_type}'. "
            f"Valid options are: 'versatile_fluo', 'versatile_he', 'paper_dsb2018', 'demo' "
            f"(with or without '2D_' prefix). "
            f"Note: 3D images are segmented slice-by-slice using 2D models."
        )

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


def stardist_2d(image, scale: float, model_type: str, model: Any | None = None):
    if model is None:
        # Get the StarDist model:
        from stardist.models import StarDist2D

        model = StarDist2D.from_pretrained(model_type)

    if model is None:
        raise RuntimeError(
            f"Failed to load StarDist model '{model_type}'. "
            f"StarDist2D.from_pretrained() returned None."
        )

    # Run StarDist:
    labels, _ = model.predict_instances(image, scale=scale)

    return labels


def stardist_3d(image, scale: float, model_type: str, min_segment_size: int):
    # Get the StarDist model once:
    from stardist.models import StarDist2D

    model = StarDist2D.from_pretrained(model_type)

    if model is None:
        raise RuntimeError(
            f"Failed to load StarDist model '{model_type}'. "
            f"StarDist2D.from_pretrained() returned None."
        )

    # Define a function to segment 2D slices:
    def segment_2d(image):
        return stardist_2d(image, scale=scale, model_type=model_type, model=model)

    segmented_image = segment_3d_from_segment_2d(
        image, segment_2d_func=segment_2d, min_segment_size=min_segment_size
    )

    return segmented_image
