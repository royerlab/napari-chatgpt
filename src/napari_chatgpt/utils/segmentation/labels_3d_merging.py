import networkx as nx
import numpy as np

def merge_2d_segments(stack, overlap_threshold: int = 1):
    # Initialize a mapping for label reassignments to manage merging
    label_mapping = {}

    # Function to update labels based on mappings
    def update_labels(plane, mapping):
        for old_label, new_label in mapping.items():
            plane[plane == old_label] = new_label
        return plane

    # Iterate through each z-plane and ensure that the labels are unique over the entire stack:
    for z in range(stack.shape[0] - 1):
        current_plane = stack[z, :, :]
        next_plane = stack[z + 1, :, :]

        # Count the number rof non-background labels in the current plane:
        current_labels = np.unique(current_plane)
        current_labels = current_labels[current_labels != 0]
        number_of_current_labels = len(current_labels)

        # Increment the id of each label in the next plane by the number of labels in the current plane except for the background label:
        next_plane[next_plane != 0] += number_of_current_labels

        # Update the stack with the incremented next plane:
        stack[z + 1, :, :] = next_plane


    # Iterate through each z-plane
    for z in range(stack.shape[0] - 1):
        current_plane = stack[z, :, :]
        next_plane = stack[z + 1, :, :]

        # Find unique labels in both planes
        current_labels = np.unique(current_plane)
        next_labels = np.unique(next_plane)

        # Check overlap for each label in the current plane
        for label in current_labels:
            if label == 0:  # Skip background
                continue

            current_mask = current_plane == label

            # Calculate overlap with next plane's segments
            for next_label in next_labels:
                if next_label == 0:  # Skip background
                    continue

                next_mask = next_plane == next_label
                overlap = np.sum(current_mask & next_mask)

                # If overlap exceeds threshold, merge segments by updating label mapping
                if overlap >= overlap_threshold:
                    label_mapping[next_label] = label
                    break  # Assuming one segment in next plane only merges with one in current

        # Update labels in the next plane based on mappings
        stack[z + 1, :, :] = update_labels(next_plane, label_mapping)

    return stack
#
# def calculate_overlaps_and_build_graph(stack):
#     G = nx.Graph()
#     # Assume stack is a 3D numpy array and overlaps is a precomputed structure
#     for z in range(stack.shape[0] - 1):
#         # Logic to calculate overlaps between current_plane and next_plane
#         # For each significant overlap, add an edge between the segments in the graph
#         pass  # Placeholder for actual implementation
#     return G
#
# def update_labels(plane, mapping):
#     """
#     Updates the labels in a 2D plane based on a given mapping.
#
#     Parameters:
#     - plane: 2D numpy array representing a single plane of the 3D stack.
#     - mapping: Dictionary with old labels as keys and new labels as values.
#
#     Returns:
#     - Updated 2D numpy array with labels reassigned based on the mapping.
#     """
#     # Create a copy of the plane to avoid modifying the original data
#     updated_plane = plane.copy()
#
#     # Iterate through the mapping and update labels
#     for old_label, new_label in mapping.items():
#         # Find pixels with the old label and assign them the new label
#         updated_plane[plane == old_label] = new_label
#
#     return updated_plane