import napari
import skimage
from arbol import aprint
from numpy import unique

from napari_chatgpt.omega.tools.napari.delegated_code.classic import \
    classic_segmentation


def test_classsic_2d(show_viewer: bool = False):
    aprint('')

    # Load the 'cells' example dataset
    cells = skimage.data.cells3d()[:, 1]

    # Maximum intensity projection:
    cells = cells.max(axis=0)

    # Segment the cells:
    labels = classic_segmentation(cells)

    # Number of unique labels:
    nb_unique_labels = len(unique(labels))

    aprint(nb_unique_labels)

    # Check that the number of unique labels is correct:
    assert nb_unique_labels == 21

    # If the viewer is not requested, return:
    if not show_viewer:
        return

    # Open a napari instance:
    viewer = napari.Viewer()

    # add image to viewer:
    viewer.add_image(cells, name='cells')

    # Load the segmented cells into the viewer:
    viewer.add_labels(labels, name='labels')

    # Make the viewer visible
    napari.run()

def test_classsic_3d(show_viewer: bool = False):
    aprint('')

    # Load the 'cells' example dataset
    cells = skimage.data.cells3d()[:, 1]

    # Segment the cells:
    labels = classic_segmentation(cells)

    # Number of unique labels:
    nb_unique_labels = len(unique(labels))

    aprint(nb_unique_labels)

    # Check that the number of unique labels is correct:
    assert nb_unique_labels == 25

    # If the viewer is not requested, return:
    if not show_viewer:
        return

    # Open a napari instance:
    viewer = napari.Viewer()

    # add image to viewer:
    viewer.add_image(cells, name='cells')

    # Load the segmented cells into the viewer:
    viewer.add_labels(labels, name='labels')

    # Make the viewer visible
    napari.run()


if __name__ == '__main__':
    test_classsic_2d(show_viewer=True)
    test_classsic_3d(show_viewer=True)