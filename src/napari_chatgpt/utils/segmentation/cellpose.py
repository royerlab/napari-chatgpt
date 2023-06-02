from typing import Sequence, Optional

from cellpose import models
from napari.types import ArrayLike


### SIGNATURE
def cellpose_segmentation(image: ArrayLike,
                          model_type: str = 'cyto',
                          channel: Optional[Sequence[int]] = None,
                          diameter: Optional[float] = None) -> ArrayLike:
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

    if channel is None:
        channel = [0, 0]

    # Load cellpose models:
    model = models.Cellpose(model_type=model_type)

    # Run cellpose:
    labels, flows, styles, diams = model.eval([image],
                                              diameter=diameter,
                                              channels=[channel])

    return labels[0]
