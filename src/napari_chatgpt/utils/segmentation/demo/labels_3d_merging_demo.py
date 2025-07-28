from typing import Optional

import napari
import skimage

from napari_chatgpt.omega_agent.tools.napari.delegated_code.stardist import stardist_2d
from napari_chatgpt.utils.images.normalize import normalize_img
from napari_chatgpt.utils.segmentation.labels_3d_merging import (
    segment_3d_from_segment_2d,
)


# Example usage
def main():
    # Load the 'cells' example dataset
    """
    Performs 3D cell segmentation on a microscopy dataset using a 2D StarDist model and visualizes the results with Napari.
    
    Loads a sample 3D cell image, normalizes its intensity, segments the volume by applying a pretrained 2D StarDist model slice-by-slice, and displays both the normalized image and segmentation labels in a Napari viewer.
    """
    cells = skimage.data.cells3d()[:, 1]

    # Normalize the image:
    norm_range_low: Optional[float] = 1.0
    norm_range_high: Optional[float] = 99.8
    cells = normalize_img(cells, norm_range_low, norm_range_high)

    # Get the StarDist model once:
    from stardist.models import StarDist2D

    model_type = "2D_versatile_fluo"
    model = StarDist2D.from_pretrained(model_type)

    def segment_2d(image):
        """
        Segment a 2D microscopy image using a StarDist model.
        
        Parameters:
            image (ndarray): A 2D image array to be segmented.
        
        Returns:
            labels (ndarray): A 2D array of integer labels representing segmented objects.
        """
        labels = stardist_2d(image, scale=1, model_type=model_type, model=model)

        return labels

    labels = segment_3d_from_segment_2d(cells, segment_2d, min_segment_size=32)

    # Open a napari instance:
    viewer = napari.Viewer()

    # add image to viewer:
    viewer.add_image(cells, name="cells")

    # Load the segmented cells into the viewer:
    viewer.add_labels(labels, name="labels")

    # Make the viewer visible
    napari.run()


if __name__ == "__main__":
    main()
