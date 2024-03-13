"""A tool for controlling a napari instance."""
import sys
import traceback
from functools import cache

from arbol import asection, aprint
from napari import Viewer

from napari_chatgpt.omega.tools.napari.delegated_code.signatures import \
    classic_signature, stardist_signature, cellpose_signature
from napari_chatgpt.omega.tools.napari.napari_base_tool import NapariBaseTool, \
    _get_delegated_code
from napari_chatgpt.utils.python.conda_utils import conda_uninstall
from napari_chatgpt.utils.python.dynamic_import import dynamic_import
from napari_chatgpt.utils.python.pip_utils import pip_install, pip_uninstall
from napari_chatgpt.omega.tools.napari.delegated_code.utils import \
    check_cellpose_installed, check_stardist_installed, \
    get_description_of_algorithms, get_list_of_algorithms


_cell_segmentation_prompt = """
"
**Context**
You are an expert python programmer with deep expertise in bioimage processing and analysis.
You are working on a project that requires you to segment cells and/or nuclei in 2D or 3D images.

**Task:**
Given a plain text request, you competently write a python function segment(viewer) that calls the 'cellpose_segmentation()', 'stardist_segmentation()' or 'classic_segmentation()' functions.
Segmentation is performed on images present as layers of the instantiated napari viewer.
The napari viewer instance is immediately available by using the variable: 'viewer'. 
For example, you can directly write: 'viewer.add_image(np.zeros((10,10)))' without preamble. 
Therefore, DO NOT use 'napari.Viewer()' or 'with napari.gui_qt():' in your code. 
DO NOT CREATE A NEW INSTANCE OF A NAPARI VIEWER, use the one provided in the variable: 'viewer'.
Make sure the calls to the viewer are correct.

**ONLY AVAILABLE SEGMENTATION FUNCTIONS:**
The only segmentation functions that you can use are 'cellpose_segmentation()', 'stardist_segmentation()' and 'classic_segmentation()':

```python
***SIGNATURES***
```

**Parameters:**
Here is an explanation of the parameters:

```docstring_fragment

    image: ArrayLike, 
            Valid parameter for both StarDist and Cellpose. 
            2D or 3D Image for which to segment cells

    model_type: str, 
            Valid parameter for both StarDist and Cellpose. 
            Segmentation model: 
            - For Cellpose it can be: cyto, nuclei. cyto -> cytoplasm (whole cell) model, nuclei -> nucleus model.
            - For StarDist can be: 'versatile_fluo', 'versatile_he'. 'versatile_fluo' is trained on a broad range of fluorescent images. 'versatile_he' is trained on H&E stained tissue (but may generalize to other staining modalities).
            
    normalize: Optional[bool]
            Valid parameter for both StarDist and Cellpose.
            If True, normalizes the image to a given percentile range.
            If False, assumes that the image is already normalized to [0,1].

    norm_range_low: Optional[float]
            Valid parameter for both StarDist and Cellpose. 
            Lower percentile for normalization

    norm_range_high: Optional[float]
            Valid parameter for both StarDist and Cellpose. 
            Higher percentile for normalization
    
    min_segment_size: Optional[int]
            Minimum number of pixels in a segment. Segments smaller than this are removed.
    
    
    channel: Optional[Sequence[int]], 
            Parameter ONLY valid for Cellpose. 
            Default is None.
            list of channels, either of length 2 or of length number of images by 2.
            First element of list is the channel to segment (0=grayscale, 1=red, 2=green, 3=blue).
            Second element of list is the optional nuclear channel (0=none, 1=red, 2=green, 3=blue).
            For instance, to segment grayscale images, input [0,0]. To segment images with cells
            in green and nuclei in blue, input [2,3]. To segment one grayscale image and one
            image with cells in green and nuclei in blue, input [[0,0], [2,3]].

    diameter: Optional[float]
            Parameter ONLY valid for Cellpose. 
            Estimated size of cells.
            if diameter is set to None, the size of the cells is estimated on a per image basis
            you can set the average cell `diameter` in pixels yourself (recommended)
            diameter can be a list or a single number for all images
            
    scale: Optional[float]
            Parameter ONLY valid for StarDist. 
            Scaling factor that gets applied to the input image before prediction.
            This is useful if the input image has a different resolution than the model was trained on.
            
    min_distance: Optional[int]
            Parameter ONLY valid for Classic.
            Minimum number of pixels separating peaks in a region of `2 * min_distance + 1`
    
    erosion_steps: Optional[int]
            Parameter ONLY valid for Classic.
            Number of iterations of the erosion operator to apply to the image.
    
    closing_steps: Optional[int]
            Parameter ONLY valid for Classic.
            Number of iterations of the closing operator to apply to the thresholded image.
    
    opening_steps: Optional[int]
            Parameter ONLY valid for Classic.
            Number of iterations of the opening operator to apply to the thresholded image.

    apply_watershed: Optional[bool]
            Parameter ONLY valid for Classic.
            If True, applies the watershed algorithm to the distance transform of the thresholded image.
            This is useful for separating cells that are touching.
```

**Notes:**
- some parameters above might refer to functions that are not available.
- All functions provided above return the segmented image as a labels array.
- When calling these functions, do not set optional parameters unless you have a good reason to change them.
- Use either ***AVAILABLE_FUNCTIONS*** directly without importing or implementing these functions, they will be provided to you by the system.
- Although StarDist or Cellpose cannot by default segment 3D images, the functions given above are capable of handling 2D *and* 3D images.

**Instructions:**
{instructions}

- If the request (below) asks for segmentation with a specific algorithm that is not available (above), then .
- Answer with a single function 'segment(viewer)->ArrayLike' that takes the viewer and returns the segmented image.

{last_generated_code}

**Viewer Information:**
{viewer_information}

**System Information:**
{system_information}

**Request:** 
{input}

**Answer in markdown:**
"""

def _get_segmentation_prompt() -> str:

    function_signatures = ''
    available_functions = ''

    if check_cellpose_installed():
        aprint("Cellpose is installed!")
        function_signatures += cellpose_signature
        available_functions += 'cellpose_segmentation() '
    if check_stardist_installed():
        aprint("Stardist is installed!")
        function_signatures += stardist_signature
        available_functions += 'stardist_segmentation() '

    function_signatures += classic_signature
    available_functions += 'classic_segmentation() '

    prompt = _cell_segmentation_prompt.replace('***SIGNATURES***', function_signatures)
    prompt = prompt.replace('***AVAILABLE_FUNCTIONS***', available_functions)

    with asection("Segmentation function signatures:"):
        aprint(function_signatures)
    with asection("Available functions:"):
        aprint(available_functions)

    return prompt

_instructions = \
"""

**Instructions specific to calling the segmentation functions:**
- DO NOT include code for the functions 'cellpose_segmentation()', 'stardist_segmentation()', or 'classic_segmentation()' in your answer.
- INSTEAD, DIRECTLY call the segmentation functions 'cellpose_segmentation()', 'stardist_segmentation()', or 'classic_segmentation()'  provided above after import.
- Assume that the functions 'cellpose_segmentation()', 'stardist_segmentation()', and 'classic_segmentation()' are available and within scope of your code.
- DO NOT add the segmentation to the napari viewer, this is done automatically by the system.
- DO NOT directly use the Cellpose or StarDist APIs: 'models.cellpose(...', 'model.predict_instances(...', etc.
- Response must be only the python function: 'segment(viewer)->ArrayLike'.
- Convert arrays to float type before processing. Intermediate or local arrays should be of type float. Constants for: np.full(), np.ones(), np.zeros(), ... should be floats (for example 1.0).
- If the request mentions 'this/that/the image/layer' then most likely it refers to the last added image or layer.
- Convert the segmented image to 'np.uint32' before returning the segmentation.
"""

class CellNucleiSegmentationTool(NapariBaseTool):
    """A tool for segmenting cells in images using different algorithms."""

    name = "CellAndNucleiSegmentationTool"
    description = (
        "Use this tool when you need to segment cells or nuclei in images (or layers). "
        f"Input must be a plain text request that must mention one of the following: {', '.join(get_list_of_algorithms())}. "
        f"{get_description_of_algorithms()}"
        "This tool operates on image layers present in the already instantiated napari viewer. "
    )
    prompt = _get_segmentation_prompt()
    instructions = _instructions
    save_last_generated_code = False

    # generic_codegen_instructions: str = ''

    def _run_code(self, request: str, code: str, viewer: Viewer) -> str:

        try:
            with asection(f"CellNucleiSegmentationTool: query= {request} "):
                # prepare code:
                code = super()._prepare_code(code,
                                             do_fix_bad_calls=self.fix_bad_calls,
                                             do_install_missing_packages=False
                                             )

                # lower case code:
                code_lower = code.lower()

                # Pick the right segmentation code:
                if 'cellpose_segmentation(' in code_lower:
                    segmentation_code = _get_delegated_code('cellpose')
                elif 'stardist_segmentation(' in code_lower:
                    segmentation_code = _get_delegated_code('stardist')
                elif 'classic_segmentation(' in code_lower:
                    segmentation_code = _get_delegated_code('classic')
                else:
                    raise ValueError(f"Could not determine the segmentation function used!")


                # combine generated code and functions:
                code = segmentation_code + '\n\n' + code

                with asection(f"Code:"):
                    aprint(code)

                # Load the code as module:
                loaded_module = dynamic_import(code)

                # get the function:
                segment = getattr(loaded_module, 'segment')

                # Run segmentation:
                with asection(f"Running segmentation..."):
                    segmented_image = segment(viewer)

                # At this point we assume the code ran successfully and we add it to the notebook:
                if self.notebook:
                    self.notebook.add_code_cell(code)


                # Add to viewer:
                viewer.add_labels(segmented_image, name='segmented')

                # Message:
                message = f"Success: image segmented and added to the viewer as a labels layer named 'segmented'."

                aprint(f"Message: {message}")

                return message

        except Exception as e:
            traceback.print_exc()
            return f"Error: {type(e).__name__} with message: '{str(e)}' occured while trying to fulfill the request. " #\n```python\n{code}\n```\n



@cache
def stardist_package_massaging() -> str:
    message = ''
    if sys.platform == 'darwin':
        with asection(f"Stardist requires special treatment on M1"):
            # purge_tensorflow()
            # conda_uninstall(['numpy', 'stardist'])
            # pip_uninstall(['numpy', 'stardist'])
            # conda_install(['tensorflow-deps'], channel='apple')
            message += pip_install(['tensorflow-macos', 'tensorflow-metal'])
            message += pip_install(['stardist'])
            #  and 'arm64' in sys.version.lower()

            return message



def purge_tensorflow():
    with asection(f"Purging the tensorflow packages from environment"):

        conda_uninstall(['tensorflow', 'tensorflow-gpu', 'tensorflow-cpu',
                         'tensorflow-deps', 'tensorflow-macos',
                         'tensorflow-metal', 'keras'])
        pip_uninstall(['tensorflow', 'tensorflow-gpu', 'tensorflow-cpu',
                       'tensorflow-deps', 'tensorflow-macos',
                       'tensorflow-metal', 'keras'])
