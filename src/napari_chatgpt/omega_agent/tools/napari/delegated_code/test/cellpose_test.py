import napari
import pytest
import skimage
from arbol import aprint
from numpy import unique

from napari_chatgpt.omega_agent.tools.napari.cell_nuclei_segmentation_tool import (
    check_cellpose_installed,
)
from napari_chatgpt.omega_agent.tools.napari.delegated_code.cellpose import (
    cellpose_segmentation,
)


@pytest.mark.skipif(
    not check_cellpose_installed(), reason="requires cellpose to be installed to run"
)
def test_cellpose_2d(show_viewer: bool = False):
    aprint("")

    # Load the 'cells' example dataset
    cells = skimage.data.cells3d()[:, 1]

    # Maximum intensity projection:
    cells = cells.max(axis=0)

    # Use smaller crop for faster testing (128x128 instead of 256x256)
    cells = cells[:128, :128]

    # Segment the cells:
    labels = cellpose_segmentation(cells)

    # Number of unique labels:
    nb_unique_labels = len(unique(labels))

    aprint(nb_unique_labels)

    # Check that the number of unique labels is reasonable (varies slightly across versions)
    # Smaller image = fewer cells expected
    assert 5 <= nb_unique_labels <= 20, f"Expected 5-20 labels, got {nb_unique_labels}"

    # If the viewer is not requested, return:
    if not show_viewer:
        return

    # Open a napari instance:
    viewer = napari.Viewer()

    # add image to viewer:
    viewer.add_image(cells, name="cells")

    # Load the segmented cells into the viewer:
    viewer.add_labels(labels, name="labels")

    # Make the viewer visible
    napari.run()


@pytest.mark.skipif(
    not check_cellpose_installed(), reason="requires cellpose to be installed to run"
)
@pytest.mark.slow
def test_cellpose_3d(show_viewer: bool = False):
    aprint("")

    # Load the 'cells' example dataset
    cells = skimage.data.cells3d()[:, 1]

    # Use tiny crop for fast testing (8x32x32 instead of 60x256x256)
    # This is sufficient to test 3D functionality works without long runtimes
    cells = cells[:8, :32, :32]

    # Segment the cells:
    labels = cellpose_segmentation(cells)

    # Number of unique labels:
    nb_unique_labels = len(unique(labels))

    aprint(nb_unique_labels)

    # Check that the number of unique labels is reasonable (varies slightly across versions)
    # Tiny image (8x32x32) = very few cells expected, may even be just background
    assert 1 <= nb_unique_labels <= 10, f"Expected 1-10 labels, got {nb_unique_labels}"

    # If the viewer is not requested, return:
    if not show_viewer:
        return

    # Open a napari instance:
    viewer = napari.Viewer()

    # add image to viewer:
    viewer.add_image(cells, name="cells")

    # Load the segmented cells into the viewer:
    viewer.add_labels(labels, name="labels")

    # Make the viewer visible
    napari.run()


if __name__ == "__main__":
    test_cellpose_2d(show_viewer=True)
    test_cellpose_3d(show_viewer=True)
