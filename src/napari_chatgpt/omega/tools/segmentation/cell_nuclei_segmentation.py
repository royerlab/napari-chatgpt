"""A tool for controlling a napari instance."""
from pathlib import Path

from napari import Viewer

from napari_chatgpt.omega.tools.napari_base_tool import NapariBaseTool
from napari_chatgpt.utils.dynamic_import import dynamic_import

_cell_segmentation_prompt = """
"
Task:
Given a plain text request, you competently write a python function segment(viewer) that calls the cellpose_segmentation() function.
Segmentation is performed on images present as layers of the instantiated napari viewer.
The napari viewer instance is immediately available by using the variable: 'viewer'. 
For example, you can directly write: viewer.add_image(np.zeros((10,10))) without preamble. 
Therefore, DO NOT use 'napari.Viewer()' or 'with napari.gui_qt():' in your code. 
DO NOT CREATE A NEW INSTANCE OF A NAPARI VIEWER, use the one provided in the variable: 'viewer'.
Make sure the calls to the viewer are correct.

{generic_codegen_instructions}

Notes: 
- Convert arrays to float type before processing. Intermediate or local arrays should be of type float. Constants for: np.full(), np.ones(), np.zeros(), ... should be floats (for example 1.0).
- If the request mentions 'this/that/the image/layer' then most likely it refers to the last added image/layer.
- Convert the segmented image to np.uint32 before returning the segmentation.


ONLY AVAILABLE SEGMENTATION FUNCTION(S):
The only segmentation function that you can use is cellpose_segmentation():

def cellpose_segmentation( image: ArrayLike,
                           model_type: str = 'cyto',
                           channel: Optional[Sequence[int]] = None,
                           diameter: Optional[float] = None) -> ArrayLike:

Here is an explanation of the parameters:
 
    image: ArrayLike, 
            Image for which to segment cells

    model_type: str, 
            Segmentation model, can be: cyto, nuclei. cyto -> cytoplasm (whole cell) model, nuclei -> nucleus model
    
    channel: Optional[Sequence[int]], 
            Default is None.
            list of channels, either of length 2 or of length number of images by 2.
            First element of list is the channel to segment (0=grayscale, 1=red, 2=green, 3=blue).
            Second element of list is the optional nuclear channel (0=none, 1=red, 2=green, 3=blue).
            For instance, to segment grayscale images, input [0,0]. To segment images with cells
            in green and nuclei in blue, input [2,3]. To segment one grayscale image and one
            image with cells in green and nuclei in blue, input [[0,0], [2,3]].

    diameter: Optional[float]
            Estimated size of cells.
            if diameter is set to None, the size of the cells is estimated on a per image basis
            you can set the average cell `diameter` in pixels yourself (recommended)
            diameter can be a list or a single number for all images

This function returns the segmented image as a labels array.
To use function cellpose_segmentation() simply import it:

from napari_chatgpt.omega.tools.segmentation.cellpose import cellpose_segmentation

IMPORTANT INSTRUCTIONS: 
- DO NOT include code for the function 'cellpose_segmentation()' in your answer.
- INSTEAD, DIRECTLY call the segmentation function 'cellpose_segmentation()' provided above after import.
- Assume that the function 'cellpose_segmentation()' is available and within scope of your code.
- DO NOT add the segmentation to the napari viewer.
- DO NOT directly use the Cellpose API: models.cellpose(...
- Response is only the python function: segment(viewer)->ArrayLike.
- The image input array to cellpose_segmentation() must be a float, therefore convert to float if needed!

Request: 
{input}

Answer in markdown with a single function segment(viewer)->ArrayLike that takes the viewer and returns the segmented image.
"""


def _get_seg_code(name: str, signature: bool = False):
    # Get package folder:
    package_folder = Path(__file__).parent

    # cellpose file path:
    file_path = Path.joinpath(package_folder, f"{name}.py")

    # code:
    code = file_path.read_text()

    # extract signature:
    if signature:
        splitted_code = code.split('### SIGNATURE')
        code = splitted_code[1]

    return code


# _cell_segmentation_prompt = _cell_segmentation_prompt.replace('*cellpose*', _get_seg_code('cellpose', signature=True))

class CellNucleiSegmentationTool(NapariBaseTool):
    """A tool for segmenting cells in images using different algorithms."""

    name = "CellAndNucleiSegmentationTool"
    description = (
        "Forward plain text requests to this tool when you need to segment cells or segment nuclei in images (or layers). "
        "This tool operates on image layers present in the already instantiated napari viewer."
        "This tool has the highest priority when the request pertains to cell or nuclei segmentation."
    )
    prompt = _cell_segmentation_prompt

    # generic_codegen_instructions: str = ''

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:
        # prepare code:
        code = super()._prepare_code(code)

        # cellpose_code = _get_seg_code('cellpose')
        #
        # # combine generated code and functions:
        # code = cellpose_code +'\n\n' + code

        # Load the code as module:
        loaded_module = dynamic_import(code)

        # get the function:
        segment = getattr(loaded_module, 'segment')

        # Run segmentation:
        segmented_image = segment(viewer)

        # Add to viewer:
        viewer.add_labels(segmented_image, name='segmented')

        return f"Success: segmentation succeeded!"
