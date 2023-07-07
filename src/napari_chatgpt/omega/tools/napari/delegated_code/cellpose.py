from typing import Sequence, Optional


from napari.types import ArrayLike
from numpy import ndarray

from napari_chatgpt.omega.tools.napari.delegated_code.classic import \
    classic_segmentation


### SIGNATURE
def cellpose_segmentation(image: ArrayLike,
                          model_type: str = 'cyto',
                          normalize: Optional[bool] = True,
                          norm_range_low: Optional[float] = 1.0,
                          norm_range_high: Optional[float] = 99.8,
                          min_segment_size: int = 32,
                          channel: Optional[Sequence[int]] = None,
                          diameter: Optional[float] = None) -> ndarray:
    """
    CP cell segmentation function.

    Parameters
    ----------

    image: ArrayLike
            image for which to segment cells

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

    # Falling back to classic segmentation if image is 3D or more:
    if len(image.shape) > 2:
        return classic_segmentation(image,
                             normalize=normalize,
                             norm_range_low=norm_range_low,
                             norm_range_high=norm_range_high)


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

    # Run cellpose:
    labels, flows, styles, diams = model.eval([image],
                                              diameter=diameter,
                                              channels=[channel])

    return labels[0]
