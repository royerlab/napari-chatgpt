"""3D instance segmentation by merging axis-aligned 2D segmentation slices."""

from collections.abc import Callable

import numpy
import numpy as np
from arbol import aprint, asection

from napari_chatgpt.utils.segmentation.remove_small_segments import (
    remove_small_segments,
)


def segment_3d_from_segment_2d(
    image,
    segment_2d_func: Callable,
    min_segment_size: int = 32,
    overlap_threshold: float = 0.5,
    iterations: int = 2,
    debug_view: bool = False,
):
    """Produce a 3D label volume by segmenting 2D slices along all three axes.

    Slices along Z, Y, and X are segmented independently with
    *segment_2d_func*, then the three binary masks are intersected.
    Morphological closing/opening cleans the mask before labels from the
    Z-axis segmentation are merged across slices based on overlap.

    Args:
        image: 3D image array of shape ``(Z, Y, X)``.
        segment_2d_func: Callable that takes a 2D image and returns a label array.
        min_segment_size: Minimum segment size in pixels; smaller segments
            are removed per slice.
        overlap_threshold: Fraction of overlap required to merge two labels
            across adjacent slices.
        iterations: Number of morphological dilation/erosion iterations for
            mask cleaning.
        debug_view: If ``True``, open a napari viewer to inspect intermediate
            merge results.

    Returns:
        3D label array with merged segment labels.
    """
    # Segment the 2D slices along z axis:
    aprint("Segmenting 2D slices along z axis")
    labels_z = segment_2d_z_slices(
        image, segment_2d_func, min_segment_size=min_segment_size
    )

    # Segment the 2D slices along y axis:
    aprint("Segmenting 2D slices along y axis")
    image = np.transpose(image, (1, 2, 0))
    labels_y = segment_2d_z_slices(
        image, segment_2d_func, min_segment_size=min_segment_size
    )

    # Transpose the labels back to the original orientation:
    labels_y = np.transpose(labels_y, (2, 0, 1))

    # Segment the 2D slices along x axis:
    aprint("Segmenting 2D slices along x axis")
    image = np.transpose(image, (1, 2, 0))
    labels_x = segment_2d_z_slices(
        image, segment_2d_func, min_segment_size=min_segment_size
    )

    # transpose the labels back to the original orientation:
    labels_x = np.transpose(labels_x, (1, 2, 0))

    # Convert the labels to binary arrays:
    binary_labels_z = labels_z > 0
    binary_labels_y = labels_y > 0
    binary_labels_x = labels_x > 0

    # Take the product of the binary arrays to get a mask:
    mask = binary_labels_z * binary_labels_y * binary_labels_x

    # Apply morphological closing operator n times to fill in the holes, and then the erosion operator n times to remove the noise:
    from skimage.morphology import dilation, erosion

    for _ in range(iterations):
        mask = dilation(mask)
    for _ in range(iterations):
        mask = erosion(mask)

    # Apply the mask to the labels:
    labels_z = labels_z * mask

    # Merge the labels from the three axes:
    labels_z = make_slice_labels_different(labels_z)

    # Merge the labels:
    labels = merge_2d_segments(
        labels_z, overlap_threshold=overlap_threshold, debug_view=debug_view
    )

    return labels


def segment_2d_z_slices(image, segment_2d_func: Callable, min_segment_size: int = 32):
    """Segment each Z-slice of a 3D image independently using a 2D function.

    Args:
        image: 3D image array of shape ``(Z, Y, X)``.
        segment_2d_func: Callable that segments a single 2D image.
        min_segment_size: Minimum segment size; smaller objects are removed.

    Returns:
        3D uint32 label array with per-slice segmentation.
    """
    # Initialize an empty list to collect the segmented slices
    segmented_slices = []

    # Iterate over each slice of the 3D image
    for i in range(image.shape[0]):
        # Segment the current slice
        # Note: We are not setting optional parameters as instructed
        segmented_slice = segment_2d_func(image[i])

        segmented_slice = remove_small_segments(
            segmented_slice, min_segment_size=min_segment_size
        )

        # Append the segmented slice to the list
        segmented_slices.append(segmented_slice)

    # Stack the segmented slices to form a 3D segmented image
    segmented_image = numpy.stack(segmented_slices, axis=0)

    # Convert the segmented image to uint32 as required
    segmented_image = segmented_image.astype(numpy.uint32)

    return segmented_image


def make_slice_labels_different(stack):
    """Re-index labels so that every Z-slice uses globally unique label IDs.

    Args:
        stack: 3D label array modified in-place.

    Returns:
        The same array with per-slice labels offset to be unique across slices.
    """
    # Max label index:
    max_label_index = 0

    # Iterate through each z-plane and ensure that the labels are unique over the entire stack:
    for z in range(stack.shape[0] - 1):
        # Save the positions of the background voxels in a binary array:
        background = stack[z, :, :] == 0

        # Add the counter to the current plane:
        stack[z, :, :] += max_label_index

        # Reset the background labels to zero:
        stack[z, :, :][background] = 0

        # Count the number of non-background labels in the current plane:
        current_labels = np.unique(stack[z, :, :])
        max_label_index = numpy.max(current_labels)

    return stack


def merge_2d_segments(stack, overlap_threshold: int = 1, debug_view: bool = True):
    """Merge labels across consecutive Z-slices based on spatial overlap.

    Adjacent slices are compared and overlapping labels exceeding
    *overlap_threshold* are unified to the smallest label ID.

    Args:
        stack: 3D label array with globally unique per-slice labels.
        overlap_threshold: Minimum overlap fraction to trigger merging.
        debug_view: If ``True``, open a napari viewer after each non-empty
            slice for inspection.

    Returns:
        The label array with merged labels.
    """
    with asection("Merging 2D segments"):

        # Iterate through each z-plane
        for z in range(stack.shape[0] - 1):

            aprint(f"Processing z-plane {z} of {stack.shape[0] - 1}")

            # Get the current and next planes
            current_plane = stack[z, :, :]
            next_plane = stack[z + 1, :, :]

            # List all unique labels in the current plane:
            current_labels = np.unique(current_plane)
            current_labels = current_labels[current_labels != 0]

            # List all unique labels in the next plane:
            next_labels = np.unique(next_plane)
            next_labels = next_labels[next_labels != 0]

            # Check overlap for each label in the next plane
            for next_label in next_labels:

                # Create a mask for the current label:
                next_mask = next_plane == next_label

                # List of overlapping labels:
                list_of_labels = []

                # Calculate overlap with next plane's segments
                for current_label in current_labels:

                    # Create a mask for the other label:
                    current_mask = current_plane == current_label

                    # Calculate the overlap between the two masks:
                    next_mask_sum = np.sum(next_mask)
                    current_mask_sum = np.sum(current_mask)
                    min_mask_sum = min(next_mask_sum, current_mask_sum)

                    # Avoid division by zero if either mask is empty:
                    if min_mask_sum == 0:
                        overlap = 0.0
                    else:
                        overlap = np.sum(next_mask & current_mask) / min_mask_sum

                    # If overlap exceeds threshold, add the label to the list:
                    if overlap >= overlap_threshold:
                        list_of_labels.append(current_label)

                # Find the smallest label in the list of overlapping labels:
                if len(list_of_labels) > 0:
                    new_label = min(next_label, min(list_of_labels))

                    # Update all the overlapping labels to the smallest label:
                    for old_label in list_of_labels:
                        if old_label != new_label:
                            stack[stack == old_label] = new_label

                    # update the label in the next plane
                    if next_label != new_label:
                        stack[stack == next_label] = new_label

            if debug_view and len(next_labels) > 0:
                # Open a napari instance:
                from napari import Viewer

                viewer = Viewer()

                # Load the segmented cells into the viewer:
                viewer.add_labels(stack, name="labels")

                # Make the viewer visible
                from napari import run

                run()

    return stack
