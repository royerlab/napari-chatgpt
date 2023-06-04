import numpy
from napari.layers import Image, Labels, Points, Vectors, Tracks, Surface, \
    Shapes


def get_viewer_layers_info(viewer):
    layer_info = []

    for index, layer in enumerate(viewer.layers):
        layer_type = type(layer).__name__
        layer_name = layer.name

        info = f"{index}. Type={layer_type}, Name={layer_name}"

        if isinstance(layer, Image):
            num_dimensions = layer.data.ndim
            shape = layer.data.shape
            dtype = layer.data.dtype
            info += f", Dimensions={num_dimensions}, Shape={shape}, Dtype={dtype}"

        elif isinstance(layer, Labels):
            num_dimensions = layer.data.ndim
            shape = layer.data.shape
            dtype = layer.data.dtype
            num_segments = len(numpy.unique(layer.data))
            info += f", Dimensions={num_dimensions}, Shape={shape}, Dtype={dtype}, Segments={num_segments} (includes background)"

        elif isinstance(layer, Points):
            num_dimensions = layer.data.ndim
            shape = layer.data.shape
            dtype = layer.data.dtype
            num_points = shape[0]
            info += f", Dimensions={num_dimensions}, Shape={shape}, Dtype={dtype}, Points={num_points}"

        elif isinstance(layer, Vectors):
            num_dimensions = layer.data.ndim
            shape = layer.data.shape
            dtype = layer.data.dtype
            num_vectors = shape[0]
            info += f", Dimensions={num_dimensions}, Shape={shape}, Dtype={dtype}, Vectors={num_vectors}"

        elif isinstance(layer, Tracks):
            num_dimensions = layer.data.ndim
            shape = layer.data.shape
            dtype = layer.data.dtype
            num_tracks = shape[0]
            info += f", Dimensions={num_dimensions}, Shape={shape}, Dtype={dtype}, Tracks={num_tracks}"

        elif isinstance(layer, Shapes):
            info += f""

        elif isinstance(layer, Surface):
            vertices, faces, values = layer.data
            num_dimensions = vertices.ndim
            dtype = vertices.dtype
            info += f", Dimensions={num_dimensions}, Num_vertices={len(vertices)}, Num_triangles={len(faces)}, Num_values={len(values)}, Dtype={dtype}"

        layer_info.append(info)

    return '\n'.join(layer_info)