"""A tool for controlling a napari instance."""

from napari import viewer, Viewer

from napari_chatgpt.tools.napari_base_tool import NapariBaseTool
from napari_chatgpt.utils.inspection import object_info_str

_napari_viewer_control_prompt = """
"
Task:
Given a plain text request, you competently write python code to control an already instantiated napari viewer instance.
The napari viewer instance is immediately available by using the variable: 'viewer'. 
For example, you can directly write: viewer.add_image(np.zeros((10,10))) without preamble. 
Therefore, DO NOT use 'napari.Viewer()' or 'with napari.gui_qt():' in your code. 
DO NOT CREATE A NEW INSTANCE OF A NAPARI VIEWER, use the one provided in the variable: 'viewer'.
Make sure the calls to the viewer are correct.

{generic_codegen_instructions}

Only use existing methods of the napari viewer:

viewer.add_layer(layer: Layer)
viewer.add_image(data: ArrayLike, rgb:bool=None, colormap='gray', contrast_limits=None, gamma=1, interpolation2d='nearest', interpolation3d='linear', rendering='mip', iso_threshold=0.5, attenuation=0.05, name=None, metadata=None, scale=None, translate=None, rotate=None, shear=None, affine=None, opacity=1, blending='translucent', visible=True, multiscale=None, cache=True, depiction='volume', plane=None, experimental_clipping_planes=None)
viewer.add_labels(data: ArrayLike, num_colors:int=50, features=None, properties=None, color=None, seed=0.5, name=None, metadata=None, scale=None, translate=None, rotate=None, shear=None, affine=None, opacity=0.7, blending='translucent', rendering='iso_categorical', depiction='volume', visible=True, multiscale=None, cache=True, plane=None, experimental_clipping_planes=None)
viewer.add_points(data: ArrayLike=None, ndim:int=None, features=None, properties=None, text=None, symbol='o', size=10, edge_width=0.05, edge_width_is_relative=True, edge_color='dimgray', edge_color_cycle=None, edge_colormap='viridis', edge_contrast_limits=None, face_color='white', face_color_cycle=None, face_colormap='viridis', face_contrast_limits=None, out_of_slice_display=False, n_dimensional=None, name=None, metadata=None, scale=None, translate=None, rotate=None, shear=None, affine=None, opacity=1, blending='translucent', visible=True, cache=True, property_choices=None, experimental_clipping_planes=None, shading='none', canvas_size_limits=(2, 10000), antialiasing=1, shown=True)
viewer.add_shapes(data: ArrayLike=None, ndim:int=None, features=None, properties=None, property_choices=None, text=None, shape_type='rectangle', edge_width=1, edge_color='#777777', edge_color_cycle=None, edge_colormap='viridis', edge_contrast_limits=None, face_color='white', face_color_cycle=None, face_colormap='viridis', face_contrast_limits=None, z_index=0, name=None, metadata=None, scale=None, translate=None, rotate=None, shear=None, affine=None, opacity=0.7, blending='translucent', visible=True, cache=True, experimental_clipping_planes=None)
viewer.add_surface(data: ArrayLike, colormap='gray', contrast_limits=None, gamma=1, name=None, metadata=None, scale=None, translate=None, rotate=None, shear=None, affine=None, opacity=1, blending='translucent', shading='flat', visible=True, cache=True, experimental_clipping_planes=None, wireframe=None, normals=None)
viewer.add_tracks(data: ArrayLike, features=None, properties=None, graph=None, tail_width=2, tail_length=30, head_length=0, name=None, metadata=None, scale=None, translate=None, rotate=None, shear=None, affine=None, opacity=1, blending='additive', visible=True, colormap='turbo', color_by='track_id', colormaps_dict=None, cache=True, experimental_clipping_planes=None)
viewer.add_vectors(data: ArrayLike=None, ndim=None, features=None, properties=None, property_choices=None, edge_width=1, edge_color='red', edge_color_cycle=None, edge_colormap='viridis', edge_contrast_limits=None, out_of_slice_display=False, length=1, name=None, metadata=None, scale=None, translate=None, rotate=None, shear=None, affine=None, opacity=0.7, blending='translucent', visible=True, cache=True, experimental_clipping_planes=None)

Note 1: To add images, labels, points, shapes, surfaces, tracks, vectors or any other type of layer,
that are not stored as an array, you might need to write additional code to read files from
disk or download 

Note 2: When operating on layers (for example applying a filter, etc.) the resulting images, labels, points, ... 
should be added ideally as new layer in napari, unless it is explicitly asked that the operation be in-place.
 
Request: 
{input}

Answer in markdown:
"""


class NapariViewerControlTool(NapariBaseTool):
    """A tool for running python code in a REPL."""

    name = "NapariViewerControlTool"
    description = (
        "Forward to this tool requests to control, operate, act, or set parameters of a napari viewer instance. "
        "Requests must be a plain text description (no code) of what must be done with the viewer, its layers, or parameters"
    )
    prompt = _napari_viewer_control_prompt.replace('***', object_info_str(
        viewer.Viewer(show=False), add_docstrings=False))

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:
        code = super()._prepare_code(code)

        # Running code:
        exec(code, globals(), {**locals(), 'viewer': viewer})

        return f"Success: request satisfied: '{query}'!"
