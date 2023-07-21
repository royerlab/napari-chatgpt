"""A tool for controlling a napari instance."""
import traceback

from arbol import asection, aprint
from napari import Viewer

from napari_chatgpt.omega.tools.napari.napari_base_tool import NapariBaseTool
from napari_chatgpt.utils.python.dynamic_import import execute_as_module
from napari_chatgpt.utils.python.exception_description import \
    exception_description
from napari_chatgpt.utils.python.fix_code_given_error import \
    fix_code_given_error_message

_napari_viewer_control_prompt = """
"
**Context**
You are an expert python programmer with deep expertise in image processing and analysis.

**Task:**
Your task is to write Python code to control an already instantiated napari viewer instance based on a plain text request. The viewer instance is accessible using the variable `viewer`, so you can directly use methods like `viewer.add_image(np.zeros((10,10)))` without any preamble.

**Request:**
{input}

{instructions}

{last_generated_code}

Make sure that the code is correct!

**Answer in markdown:**
"""

# """
# **Use the existing methods of the `napari` viewer, which are as follows:**
# - `viewer.add_layer(layer: Layer)`
# - `viewer.add_image(data: ArrayLike, rgb:bool=None, colormap='gray', contrast_limits=None, gamma=1, interpolation2d='nearest', interpolation3d='linear', rendering='mip', iso_threshold=0.5, attenuation=0.05, name=None, metadata=None, scale=None, translate=None, rotate=None, shear=None, affine=None, opacity=1, blending='translucent', visible=True, multiscale=None, cache=True, depiction='volume', plane=None, experimental_clipping_planes=None)`
# - `viewer.add_labels(data: ArrayLike, num_colors:int=50, features=None, properties=None, color=None, seed=0.5, name=None, metadata=None, scale=None, translate=None, rotate=None, shear=None, affine=None, opacity=0.7, blending='translucent', rendering='iso_categorical', depiction='volume', visible=True, multiscale=None, cache=True, plane=None, experimental_clipping_planes=None)`
# - `viewer.add_points(data: ArrayLike=None, ndim:int=None, features=None, properties=None, text=None, symbol='o', size=10, edge_width=0.05, edge_width_is_relative=True, edge_color='dimgray', edge_color_cycle=None, edge_colormap='viridis', edge_contrast_limits=None, face_color='white', face_color_cycle=None, face_colormap='viridis', face_contrast_limits=None, out_of_slice_display=False, n_dimensional=None, name=None, metadata=None, scale=None, translate=None, rotate=None, shear=None, affine=None, opacity=1, blending='translucent', visible=True, cache=True, property_choices=None, experimental_clipping_planes=None, shading='none', canvas_size_limits=(2, 10000), antialiasing=1, shown=True)`
# - `viewer.add_shapes(data: ArrayLike=None, ndim:int=None, features=None, properties=None, property_choices=None, text=None, shape_type='rectangle', edge_width=1, edge_color='#777777', edge_color_cycle=None, edge_colormap='viridis', edge_contrast_limits=None, face_color='white', face_color_cycle=None, face_colormap='viridis', face_contrast_limits=None, z_index=0, name=None, metadata=None, scale=None, translate=None, rotate=None, shear=None, affine=None, opacity=0.7, blending='translucent', visible=True, cache=True, experimental_clipping_planes=None)`
# - `viewer.add_surface(data: ArrayLike, colormap='gray', contrast_limits=None, gamma=1, name=None, metadata=None, scale=None, translate=None, rotate=None, shear=None, affine=None, opacity=1, blending='translucent', shading='flat', visible=True, cache=True, experimental_clipping_planes=None, wireframe=None, normals=None)`
# - `viewer.add_tracks(data: ArrayLike, features=None, properties=None, graph=None, tail_width=2, tail_length=30, head_length=0, name=None, metadata=None, scale=None, translate=None, rotate=None, shear=None, affine=None, opacity=1, blending='additive', visible=True, colormap='turbo', color_by='track_id', colormaps_dict=None, cache=True, experimental_clipping_planes=None)`
# - `viewer.add_vectors(data: ArrayLike=None, ndim=None, features=None, properties=None, property_choices=None, edge_width=1, edge_color='red', edge_color_cycle=None, edge_colormap='viridis', edge_contrast_limits=None, out_of_slice_display=False, length=1, name=None, metadata=None, scale=None, translate=None, rotate=None, shear=None, affine=None, opacity=0.7, blending='translucent', visible=True, cache=True, experimental_clipping_planes=None)`
#
# """

_instructions = \
"""
**Instructions specific to controlling the viewer:**
- If you need to add images, labels, points, shapes, surfaces, tracks, vectors, or any other type of layer that is not stored as an array, you may need additional code to read files from disk or download from a URL.
- Unless explicitly stated in the request, the result of operations on layers should be a new layer in napari and should not modify the existing layers.
- Convert image arrays to the float type before processing. Intermediate or local image arrays should be of type float. Constants like `np.full()`, `np.ones()`, `np.zeros()`, etc., should be floats (e.g., 1.0).
- If the request mentions "this," "that," or "the image/layer," it most likely refers to the last added image/layer.
- If you are unsure about the layer being referred to, assume it is the last layer of the type most appropriate for the request.
- If the request mentions the 'selected image', it most likely refers to the active or selected image layer.
- To get the selected layer use: viewer.layers.selection.active
- Important: At the end of your code add a print statement that states clearly and concisely what has been, or not, achieved. 
- Do not create a new instance of `napari.Viewer()`. Use the existing instance provided in the variable `viewer`.
- Ensure that your calls to the viewer's methods are correct.
"""

_code_prefix = \
"""
import napari
"""

class NapariViewerControlTool(NapariBaseTool):
    """A tool for running python code in a REPL."""

    name = "NapariViewerControlTool"
    description = (
        "Use this tool when you want to control, operate, perform actions, "
        "or adjust parameters of a napari viewer instance or its layers "
        "(images, labels, points, tracks, shapes, and meshes). "
        "Input must be a plain text description of what you want to do. "
        "The input must not assume knowledge of our conversation and must be explicit about what is asked."
        "For instance, you can request to 'apply a Gaussian filter to the selected image'. "
        "Do NOT include code in your input."
    )
    prompt = _napari_viewer_control_prompt
    instructions = _instructions
    code_prefix = _code_prefix
    save_last_generated_code = False

    def _run_code(self, request: str, code: str, viewer: Viewer) -> str:

        try:
            with asection(f"NapariViewerControlTool: request= {request} "):

                # Prepare code:
                code = super()._prepare_code(code, do_fix_bad_calls=self.fix_bad_calls)

                captured_output = self._run_code_catch_errors_fix_and_try_again(code,
                                                                           viewer=viewer,
                                                                           instructions=self.instructions,
                                                                           )

                # Message:
                if len(captured_output) > 0:
                    message = f"Tool completed task successfully: {captured_output}"
                else:
                    message = f"Tool completed task successfully"

                with asection(f"Message:"):
                    aprint(message)

                return message

        except Exception as e:
            traceback.print_exc()
            return f"Error: {type(e).__name__} with message: '{str(e)}' occured while fullfiling request. " #\n```python\n{code}\n```\n



    def _run_code_catch_errors_fix_and_try_again(self,
                                                 code,
                                                 viewer,
                                                 error:str = '',
                                                 instructions:str = '',
                                                 nb_tries: int = 3) -> str:

        try:
            with asection(f"Running code:"):
                aprint(f"Code:\n{code}")
                captured_output = execute_as_module(code, viewer=viewer)
                aprint(f"This is what the code returned:\n{captured_output}")

        except Exception as e:
            if nb_tries >= 1:
                traceback.print_exc()
                description = error+'\n\n'+exception_description(e)
                description = description.strip()
                fixed_code = fix_code_given_error_message(code=code,
                                                          error=description,
                                                          instructions=instructions,
                                                          viewer=viewer,
                                                          llm=self.llm,
                                                          verbose=self.verbose)
                # We try again:
                return self._run_code_catch_errors_fix_and_try_again(fixed_code,
                                                                viewer=viewer,
                                                                error=error,
                                                                nb_tries = nb_tries-1)
            else:
                # No more tries available, we give up!
                raise e


        return captured_output
