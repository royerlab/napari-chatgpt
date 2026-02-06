"""Utility function for removing small segments from label images."""

from numpy import ndarray


def remove_small_segments(labels: ndarray, min_segment_size: int) -> ndarray:
    """
    Remove small segments from a labels array.

    Parameters
    ----------
    labels : ndarray
        Label image where each segment has a unique integer value.
    min_segment_size : int
        Minimum number of pixels/voxels in a segment. Segments smaller than
        this are removed (set to 0).

    Returns
    -------
    ndarray
        Label image with small segments removed.
    """
    if min_segment_size > 0:
        from skimage.morphology import remove_small_objects

        labels = remove_small_objects(labels, min_segment_size)
    return labels
