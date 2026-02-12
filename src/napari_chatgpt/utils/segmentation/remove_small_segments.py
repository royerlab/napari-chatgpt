"""Utility function for removing small segments from label images."""

from numpy import ndarray


def remove_small_segments(labels: ndarray, min_segment_size: int) -> ndarray:
    """Remove small segments from a labels array.

    Args:
        labels: Label image where each segment has a unique integer value.
        min_segment_size: Minimum number of pixels/voxels in a segment.
            Segments smaller than this are removed (set to 0).

    Returns:
        Label image with small segments removed.
    """
    if min_segment_size > 0:
        from skimage.morphology import remove_small_objects

        labels = remove_small_objects(labels, max_size=min_segment_size - 1)
    return labels
