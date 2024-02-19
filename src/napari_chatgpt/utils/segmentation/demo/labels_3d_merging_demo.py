import sys

import napari
import numpy
import skimage
from arbol import aprint
from qtpy.QtWidgets import QApplication

from napari_chatgpt.utils.qt.one_time_disclaimer_dialog import \
    show_one_time_disclaimer_dialog

# Example usage
def main():

    # Open a napari instance:
    viewer = napari.Viewer()

    # Load the 'cells' example dataset
    cells = skimage.data.cells3d()[:, 1]

    # add image to viewer:
    viewer.add_image(cells, name='cells')

    # Segment the cells using StarDist:
    from napari_chatgpt.omega.tools.napari.delegated_code.stardist import \
        stardist_segmentation
    labels = stardist_segmentation(cells, normalize=True)

    # Load the segmented cells into the viewer:
    viewer.add_labels(labels, name='labels')

    # Make the viewer visible
    napari.run()


if __name__ == '__main__':
    main()