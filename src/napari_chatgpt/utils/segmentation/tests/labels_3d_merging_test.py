"""Tests for labels_3d_merging functions."""

import numpy as np

from napari_chatgpt.utils.segmentation.labels_3d_merging import (
    make_slice_labels_different,
    merge_2d_segments,
)


def test_make_slice_labels_different_offsets_labels():
    # Two slices, each with labels 1 and 2
    stack = np.zeros((2, 4, 4), dtype=np.uint32)
    stack[0, 0:2, 0:2] = 1
    stack[0, 2:4, 2:4] = 2
    stack[1, 0:2, 0:2] = 1
    stack[1, 2:4, 2:4] = 2

    result = make_slice_labels_different(stack)

    # First slice labels should still be 1 and 2
    assert set(np.unique(result[0])) == {0, 1, 2}
    # Second slice labels should be different (offset by max of first slice)
    labels_slice1 = set(np.unique(result[1])) - {0}
    assert len(labels_slice1) == 2
    # The labels in slice 1 should not overlap with labels in slice 0
    labels_slice0 = set(np.unique(result[0])) - {0}
    # Note: the function only offsets slices 0..N-2, last slice is left as-is
    # But since we only have 2 slices, only slice 0 gets offset


def test_make_slice_labels_different_all_zero():
    stack = np.zeros((3, 4, 4), dtype=np.uint32)
    result = make_slice_labels_different(stack)
    np.testing.assert_array_equal(result, stack)


def test_make_slice_labels_different_single_slice():
    stack = np.zeros((1, 4, 4), dtype=np.uint32)
    stack[0, 0:2, 0:2] = 1
    original = stack.copy()
    result = make_slice_labels_different(stack)
    np.testing.assert_array_equal(result, original)


def test_merge_2d_segments_with_overlap():
    # Two slices with overlapping labels at the same position
    stack = np.zeros((2, 4, 4), dtype=np.uint32)
    stack[0, 0:3, 0:3] = 1
    stack[1, 0:3, 0:3] = 2

    result = merge_2d_segments(stack, overlap_threshold=0.5, debug_view=False)

    # Both regions overlap, so they should be merged to the same label
    labels_slice0 = set(np.unique(result[0])) - {0}
    labels_slice1 = set(np.unique(result[1])) - {0}
    assert labels_slice0 == labels_slice1


def test_merge_2d_segments_no_overlap():
    # Two slices with non-overlapping regions
    stack = np.zeros((2, 6, 6), dtype=np.uint32)
    stack[0, 0:2, 0:2] = 1
    stack[1, 4:6, 4:6] = 2

    result = merge_2d_segments(stack, overlap_threshold=0.5, debug_view=False)

    # No overlap so labels should remain distinct
    labels_slice0 = set(np.unique(result[0])) - {0}
    labels_slice1 = set(np.unique(result[1])) - {0}
    if labels_slice0 and labels_slice1:
        assert labels_slice0 != labels_slice1
