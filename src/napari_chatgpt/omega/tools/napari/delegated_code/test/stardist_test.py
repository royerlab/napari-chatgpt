import napari
import pytest
import skimage
from arbol import aprint
from numpy import unique

from napari_chatgpt.omega.tools.napari.cell_nuclei_segmentation_tool import \
    check_stardist_installed
from napari_chatgpt.omega.tools.napari.delegated_code.stardist import \
    stardist_segmentation


@pytest.mark.skipif(not check_stardist_installed(),
                    reason="requires stardist to be installed to run")
def test_stardist_2d(show_viewer: bool = False):
    aprint('')

    # Load the 'cells' example dataset
    cells = skimage.data.cells3d()[:, 1]

    # Maximum intensity projection:
    cells = cells.max(axis=0)

    # Segment the cells:
    labels = stardist_segmentation(cells)

    # Number of unique labels:
    nb_unique_labels = len(unique(labels))

    aprint(nb_unique_labels)

    # Check that the number of unique labels is correct:
    assert nb_unique_labels == 22

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

@pytest.mark.skipif(not check_stardist_installed(),
                    reason="requires stardist to be installed to run")
def test_stardist_3d(show_viewer: bool = False):
    aprint('')

    # Load the 'cells' example dataset
    cells = skimage.data.cells3d()[:, 1]

    # Segment the cells:
    labels = stardist_segmentation(cells)

    # Number of unique labels:
    nb_unique_labels = len(unique(labels))

    aprint(nb_unique_labels)

    # Check that the number of unique labels is correct:
    assert nb_unique_labels == 27

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
    test_stardist_2d(show_viewer=True)
    test_stardist_3d(show_viewer=True)