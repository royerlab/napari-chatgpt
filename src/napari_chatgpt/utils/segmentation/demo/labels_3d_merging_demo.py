from typing import Optional

import napari
import skimage

from napari_chatgpt.omega.tools.napari.delegated_code.stardist import \
    stardist_2d
from napari_chatgpt.utils.segmentation.labels_3d_merging import \
    segment_3d_from_segment_2d
from napari_chatgpt.utils.images.normalize import normalize_img

# Example usage
def main():


    # Load the 'cells' example dataset
    cells = skimage.data.cells3d()[:, 1]

    # Normalize the image:
    norm_range_low: Optional[float] = 1.0
    norm_range_high: Optional[float] = 99.8
    cells = normalize_img(cells, norm_range_low, norm_range_high)

    # Get the StarDist model once:
    from stardist.models import StarDist2D
    model_type = '2D_versatile_fluo'
    model = StarDist2D.from_pretrained(model_type)

    def segment_2d(image):

        labels = stardist_2d(image,
                             scale=1,
                             model_type=model_type,
                             model=model)

        return labels

    labels = segment_3d_from_segment_2d(cells,
                                        segment_2d,
                                        min_segment_size=32)

    # Open a napari instance:
    viewer = napari.Viewer()

    # add image to viewer:
    viewer.add_image(cells, name='cells')

    # Load the segmented cells into the viewer:
    viewer.add_labels(labels, name='labels')

    # Make the viewer visible
    napari.run()


if __name__ == '__main__':
    main()