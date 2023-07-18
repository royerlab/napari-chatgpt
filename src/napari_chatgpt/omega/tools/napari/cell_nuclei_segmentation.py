"""A tool for controlling a napari instance."""
import sys
import traceback
from functools import cache
from pathlib import Path

from arbol import asection, aprint
from napari import Viewer

from napari_chatgpt.omega.tools.napari.napari_base_tool import NapariBaseTool, \
    _get_delegated_code
from napari_chatgpt.utils.python.conda_utils import conda_uninstall
from napari_chatgpt.utils.python.dynamic_import import dynamic_import
from napari_chatgpt.utils.python.pip_utils import pip_install, pip_uninstall

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
def cellpose_segmentation( image: ArrayLike,
                           model_type: str = 'cyto',
                           normalize: Optional[bool] = True,
                           norm_range_low: Optional[float] = 1.0,
                           norm_range_high: Optional[float] = 99.8,
                           min_segment_size: int = 32,
                           channel: Optional[Sequence[int]] = None,
                           diameter: Optional[float] = None) -> ArrayLike
                           
def stardist_segmentation(image: ArrayLike,
                          model_type: str = '2D_versatile_fluo',
                          normalize: Optional[bool] = True,
                          norm_range_low: Optional[float] = 1.0,
                          norm_range_high: Optional[float] = 99.8,
                          min_segment_size: int = 32,
                          scale:float = None) -> ArrayLike
                          
def classic_segmentation(image: ArrayLike,
                          threshold_type: str = 'otsu',
                          normalize: Optional[bool] = True,
                          norm_range_low: Optional[float] = 1.0,
                          norm_range_high: Optional[float] = 99.8,
                          min_segment_size: int = 32,
                          erosion_steps: int = 1,
                          closing_steps: int = 1,
                          opening_steps: int = 0,
                          apply_watershed: bool = False,
                          min_distance: int = 10) -> ArrayLike:
```

StarDist is better for segmenting nearly convex nuclei whereas Cellpose is better for segmenting non-convex cells, in particular their cytoplasm. 
StarDist and Cellpose are deep learning based methods that only work in 2D and are better for small images. 
Classic segmentation is a simple thresholding method that can be used as a baseline and works in 3D and more dimensions.

Here is an explanation of the parameters:

```docstring_fragment

    image: ArrayLike, 
            Valid parameter for both StarDist and Cellpose. 
            Image for which to segment cells

    model_type: str, 
            Valid parameter for both StarDist and Cellpose. 
            Segmentation model: 
            - For Cellpose it can be: cyto, nuclei. cyto -> cytoplasm (whole cell) model, nuclei -> nucleus model.
            - For StarDist can be: '2D_versatile_fluo', '2D_versatile_he', '3D_versatile_fluo'. '2D_versatile_fluo' is trained on a broad range of fluorescent 2D semantic
            segmentation images. '2D_versatile_he' is trained on H&E stained tissue (but may generalize to other
            staining modalities). '3D_versatile_fluo' is trained for 3D fluorescence microscopy images.
            
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

All functions provided above return the segmented image as a labels array.
When calling these functions, do not set optional parameters unless you have a good reason to change them.
Use either 'cellpose_segmentation()', 'stardist_segmentation()' or 'classic_segmentation()' directly without importing or implementing these functions, they will be provided to you by the system.

{instructions}

{last_generated_code}

Request: 
{input}

Answer in markdown with a single function 'segment(viewer)->ArrayLike' that takes the viewer and returns the segmented image.
"""

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
        "Input must be a plain text request that must mention 'cellpose', 'stardist' or 'classic'. "
        "For example, you can request to: 'segment cell nuclei in selected layer with StarDist', 'segment cell's cytoplams in selected layer with Cellpose', or 'segment cell nuclei in selected 3D image with Classic'. "
        "Choose StarDist for nuclei, cellpose for teh cell cytoplasm/membrane outline, and Classic for 3D images. "
        "This tool operates on image layers present in the already instantiated napari viewer. "
    )
    prompt = _cell_segmentation_prompt
    instructions = _instructions
    save_last_generated_code = False

    # generic_codegen_instructions: str = ''

    def _run_code(self, request: str, code: str, viewer: Viewer) -> str:

        try:
            with asection(f"CellNucleiSegmentationTool: query= {request} "):
                # prepare code:
                code = super()._prepare_code(code, do_fix_bad_calls=self.fix_bad_calls)

                # lower case code:
                code_lower = code.lower()

                # Pick the right segmentation code:
                if 'cellpose_segmentation(' in code_lower:
                    segmentation_code = _get_delegated_code('cellpose')
                elif 'stardist_segmentation(' in code_lower:
                    segmentation_code = _get_delegated_code('stardist')
                    # Check if we are on M1:
                    stardist_package_massaging()
                elif 'classic_segmentation(' in code_lower:
                    segmentation_code = _get_delegated_code('cellpose')
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

                # Add to viewer:
                viewer.add_labels(segmented_image, name='segmented')

                # Message:
                message = f"Success: image segmented and added to the viewer as a labels layer named 'denoised'."

                aprint(f"Message: {message}")

                return message

        except Exception as e:
            traceback.print_exc()
            return f"Error: {type(e).__name__} with message: '{str(e)}' occured while trying to fulfill the request. " #\n```python\n{code}\n```\n



@cache
def stardist_package_massaging():
    if sys.platform == 'darwin':
        with asection(f"Stardist requires special treatment on M1"):
            # purge_tensorflow()
            # conda_uninstall(['numpy', 'stardist'])
            # pip_uninstall(['numpy', 'stardist'])
            # conda_install(['tensorflow-deps'], channel='apple')
            pip_install(['tensorflow-macos', 'tensorflow-metal'])
            pip_install(['stardist'])
            #  and 'arm64' in sys.version.lower()


def purge_tensorflow():
    with asection(f"Purging the tensorflow packages from environment"):

        conda_uninstall(['tensorflow', 'tensorflow-gpu', 'tensorflow-cpu',
                         'tensorflow-deps', 'tensorflow-macos',
                         'tensorflow-metal', 'keras'])
        pip_uninstall(['tensorflow', 'tensorflow-gpu', 'tensorflow-cpu',
                       'tensorflow-deps', 'tensorflow-macos',
                       'tensorflow-metal', 'keras'])
