from collections.abc import Sequence

from napari.types import ArrayLike
from numpy import ndarray

from napari_chatgpt.utils.segmentation.remove_small_segments import (
    remove_small_segments,
)


### SIGNATURE
def cellpose_segmentation(
    image: ArrayLike,
    model_type: str = "cyto",
    normalize: bool | None = True,
    norm_range_low: float | None = 1.0,
    norm_range_high: float | None = 99.8,
    min_segment_size: int = 32,
    channel: Sequence[int] | None = None,
    diameter: float | None = None,
) -> ndarray:
    """
    CP cell segmentation function.

    Parameters
    ----------

    image: ArrayLike
            image for which to segment cells, must be 2D or 3D.

    model_type: str
            Model type, can be: 'cyto' or 'nuclei' or 'cyto2'.
            'cyto'=cytoplasm (whole cell) model;
            'nuclei'=nucleus model;
            'cyto2'=cytoplasm (whole cell) model with additional user images

    normalize: Optional[bool]
            If True, normalizes the image to a given percentile range.
            If False, assumes that the image is already normalized to [0,1].

    norm_range_low: Optional[float]
            Lower percentile for normalization

    norm_range_high: Optional[float]
            Higher percentile for normalization

    min_segment_size: Optional[int]
            Minimum number of pixels in a segment. Segments smaller than this are removed.

    channel: Optional[Sequence[int]]
            Default is None.
            list of channels, either of length 2 or of length number of images by 2.
            First element of list is the channel to segment (0=grayscale, 1=red, 2=green, 3=blue).
            Second element of list is the optional nuclear channel (0=none, 1=red, 2=green, 3=blue).
            For instance, to segment grayscale images, input [0,0]. To segment images with cells
            in green and nuclei in blue, input [2,3]. To segment one grayscale image and one
            image with cells in green and nuclei in blue, input [[0,0], [2,3]].

    diameter: Optional[float]
            Estimated size of cells.
            if diameter is set to None, the size of the cells is estimated on a per image basis
            you can set the average cell `diameter` in pixels yourself (recommended)
            diameter can be a list or a single number for all images

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

    if channel is None:
        channel = [0, 0]

    # Load cellpose models:
    # Try to use GPU if available
    import torch
    from cellpose import models

    gpu = torch.cuda.is_available()
    model = models.CellposeModel(model_type=model_type, gpu=gpu)

    if len(image.shape) == 2:
        # Run cellpose in 2D mode:
        labels = model.eval(
            image, diameter=diameter, channels=channel, min_size=min_segment_size
        )[0]
    elif len(image.shape) == 3:

        # If no diameter is provided, use a default value:
        if diameter is None:
            diameter = 30.0

        # Run cellpose in 3D mode:
        labels = model.eval(
            image,
            diameter=diameter,
            channels=channel,
            do_3D=True,
            z_axis=0,
            min_size=min_segment_size,
        )[0]

    # Remove small segments:
    labels = remove_small_segments(labels, min_segment_size)

    return labels
