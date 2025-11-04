from typing import Callable

import numpy
import numpy as np
from arbol import aprint, asection


def segment_3d_from_segment_2d(
    image,
    segment_2d_func: Callable,
    min_segment_size: int = 32,
    overlap_threshold: float = 0.5,
    iterations: int = 2,
    debug_view: bool = False,
):
    # Segment the 2D slices along z axis:
    """
    Performs 3D image segmentation by applying a 2D segmentation function along all three principal axes and merging the results.
    
    This function segments 2D slices of a 3D image along the z, y, and x axes using the provided 2D segmentation function. The resulting segmentations are combined into a consensus mask using logical operations and refined with morphological closing and erosion. Unique labels are enforced across slices, and overlapping segments are merged based on a specified overlap threshold.
    
    Parameters:
        image (np.ndarray): The 3D image to segment.
        segment_2d_func (Callable): Function to segment individual 2D slices.
        min_segment_size (int, optional): Minimum segment size to retain. Defaults to 32.
        overlap_threshold (float, optional): Minimum overlap ratio for merging segments. Defaults to 0.5.
        iterations (int, optional): Number of morphological closing and erosion iterations. Defaults to 2.
        debug_view (bool, optional): If True, enables visualization during merging. Defaults to False.
    
    Returns:
        np.ndarray: 3D array of labeled segments after merging and refinement.
    """
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
    from skimage.morphology import binary_dilation, binary_erosion

    for _ in range(iterations):
        mask = binary_dilation(mask)
    for _ in range(iterations):
        mask = binary_erosion(mask)

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
    # Initialize an empty list to collect the segmented slices
    """
    Applies a 2D segmentation function to each slice along the z-axis of a 3D image and removes small segments.
    
    Parameters:
        image (numpy.ndarray): 3D image array to segment.
        segment_2d_func (Callable): Function to segment individual 2D slices.
        min_segment_size (int): Minimum segment size to retain in each slice.
    
    Returns:
        numpy.ndarray: 3D array of segmented labels with small segments removed.
    """
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


def remove_small_segments(labels, min_segment_size):
    # remove small segments:
    """
    Remove connected components smaller than a specified size from a labeled array.
    
    Parameters:
        labels: A 2D or 3D labeled array where each unique integer represents a segment.
        min_segment_size: Minimum number of pixels or voxels required for a segment to be retained.
    
    Returns:
        A labeled array with small segments removed.
    """
    if min_segment_size > 0:
        from skimage.morphology import remove_small_objects

        labels = remove_small_objects(labels, min_segment_size)
    return labels


def make_slice_labels_different(stack):
    # Max label index:
    """
    Assigns unique label indices to each slice in a 3D labeled stack to prevent label collisions across slices.
    
    Parameters:
        stack (ndarray): 3D array of labeled slices.
    
    Returns:
        ndarray: 3D labeled array with unique labels for each slice.
    """
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
    """
    Merge overlapping labeled segments between consecutive slices in a 3D stack based on a specified overlap threshold.
    
    Segments in adjacent slices are merged if their overlap ratio exceeds the given threshold, ensuring consistent labeling across the stack. Optionally, a napari viewer can be launched for visual inspection during the merging process.
    
    Parameters:
        stack (np.ndarray): 3D labeled array where each slice contains integer segment labels.
        overlap_threshold (int): Minimum overlap ratio required to merge segments between slices.
        debug_view (bool): If True, launches a napari viewer to visualize the merging process.
    
    Returns:
        np.ndarray: 3D labeled array with merged segments across slices.
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
                    overlap = np.sum(next_mask & current_mask) / min(
                        np.sum(next_mask), np.sum(current_mask)
                    )

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
