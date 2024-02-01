"""A tool for controlling a napari instance."""
import platform
import sys
import traceback
from functools import cache

from arbol import asection, aprint
from napari import Viewer

from napari_chatgpt.omega.tools.napari.napari_base_tool import NapariBaseTool, \
    _get_delegated_code
from napari_chatgpt.utils.python.dynamic_import import dynamic_import
from napari_chatgpt.utils.python.pip_utils import pip_install

_image_denoising_prompt = """
"
**Context**
You are an expert python programmer with deep expertise in image processing and analysis.
You are working on a project that requires you to denoise images.

**Task:**
Given a plain text request, you competently write a python function 'denoise(viewer)' that calls the 'aydin_classic_denoise()' or 'aydin_fgr_denoise()' functions.
Denoising is performed on images present as layers of the instantiated napari viewer.
The napari viewer instance is immediately available by using the variable: 'viewer'. 
For example, you can directly write: 'viewer.add_image(np.zeros((10,10)))' without preamble. 
Therefore, DO NOT use 'napari.Viewer()' or 'with napari.gui_qt():' in your code. 
DO NOT CREATE A NEW INSTANCE OF A NAPARI VIEWER, use the one provided in the variable: 'viewer'.
Make sure the calls to the viewer are correct.

**ONLY AVAILABLE DENOISING FUNCTION(S):**
The only denoising function that you can use are 'aydin_classic_denoise()' or 'aydin_fgr_denoise()':

```python
def aydin_classic_denoising(   image: ArrayLike,
                               batch_axes: Tuple[int] = None, 
                               chan_axes: Tuple[int] = None, 
                               variant: str = None) -> ArrayLike
                               
def aydin_fgr_denoising(       image: ArrayLike,
                               batch_axes: Tuple[int] = None, 
                               chan_axes: Tuple[int] = None,
                               variant: str = None) -> ArrayLike                             
```

In general, first try to denoise images with 'aydin_classic_denoising()' with Butterworth variant, 
and if that does not work well, try 'aydin_fgr_denoising()' with cb variant.

**Parameters:**
Here is an explanation of the parameters:
 
```docstring_fragment

    image : numpy.ndarray
        Image to denoise
    batch_axes : array_like, optional
        Indices of batch axes. Batch dimensions/axes are dimensions/axes for which there is no-spatiotemporal correlation in the data. For example: different instance images stored in the same array.
    chan_axes : array_like, optional
        Indices of channel axes. This is the dimensions/axis of the numpy array that corresponds to the channel dimension of the image. Dimensions/axes that are not batch or channel dimensions are your standard X,Y,Z or T dimensions over which the data exhibits some spatiotemporal correlation.
    variant : str
        Algorithm variant: 
        For 'aydin_classic_denoising()' may be:  'butterworth'(best combination of speed and denoising performance), 'bilateral', 'gaussian', 'gm', 'harmonic', 'nlm', 'pca', 'spectral', 'tv', 'wavelet'.
        For 'aydin_fgr_denoising()' may be: 'cb'(best), 'lgbm'(slower than cb), 'linear'(very fast but poor denoising performance), or 'random_forest'(fast and ok denoising).

```

**Instructions:**
- The function provided above returns the denoised image.
- When calling these functions, do not set optional parameters unless you have a good reason to change them.
- Use 'aydin_classic_denoising()' or 'aydin_fgr_denoising()' directly without importing or implementing that function, it is provided to you by the system.

{instructions}

- Answer in markdown with a single function 'denoise(viewer)->ArrayLike' that takes the viewer and returns the denoised image.
- Make sure that the code is correct!

{last_generated_code}

**ViewerInformation:**
{viewer_information}

**Request:** 
{input}

**Answer in markdown:**
"""

_instructions = \
"""

**Instructions specific to calling the denoising functions:**
- DO NOT include code for the functions 'aydin_classic_denoising()' and 'aydin_fgr_denoising()' in your answer.
- INSTEAD, DIRECTLY call the denoising functions 'aydin_classic_denoising()' or 'aydin_fgr_denoising()' provided above after import.
- Assume that the denoising functions 'aydin_classic_denoising()' and 'aydin_fgr_denoising()' are available and within scope of your code.
- DO NOT add the denoised image to the napari viewer, this is done automatically by the system.
- DO NOT directly use the Aydin API, only use the 'aydin_classic_denoising()' or 'aydin_fgr_denoising()' functions!
- DO NOT use functions from skimage.restoration or any other denoising library, only use the 'aydin_classic_denoising()' or 'aydin_fgr_denoising()' functions!
- Response must be only the python function: 'denoise(viewer)->ArrayLike'.
- If the request mentions 'this/that/the image/layer' then most likely it refers to the last added image or layer.
"""

class ImageDenoisingTool(NapariBaseTool):
    """A tool for denoising images using different algorithms."""

    name = "ImageDenoisingTool"
    description = (
        "Use this tool when you need to denoise nD images. "
        "Input must be a plain text request that must mention 'Aydin's classic' or 'Aydin's FGR' approaches. "
        "For example, you can request to: 'denoise the image on the selected layer with Aydin's FGR approach', or 'denoise layer named `noisy` with Aydin's classic butterworth approach'. "
        "Aydin is a feature-rich and fast nD image denoising library. "
        "This tool operates on image layers present in the already instantiated napari viewer. "
    )
    prompt = _image_denoising_prompt
    instructions = _instructions
    save_last_generated_code = False

    # generic_codegen_instructions: str = ''

    def _run_code(self, request: str, code: str, viewer: Viewer) -> str:

        try:
            with asection(f"ImageDenoisingTool: query= {request} "):
                # prepare code:
                code = super()._prepare_code(code, do_fix_bad_calls=self.fix_bad_calls)

                # lower case code:
                code_lower = code.lower()

                # Pick the right denoising code:
                if 'aydin_classic_denoising(' in code_lower:
                    install_aydin()
                    denoising_code = _get_delegated_code('aydin_classic')
                elif 'aydin_fgr_denoising(' in code_lower:
                    install_aydin()
                    denoising_code = _get_delegated_code('aydin_fgr')
                else:
                    raise ValueError(f"Could not determine the denoising function used!")

                # combine generated code and functions:
                code = denoising_code + '\n\n' + code

                with asection(f"Code:"):
                    aprint(code)

                # Load the code as module:
                loaded_module = dynamic_import(code)

                # get the function:
                denoise = getattr(loaded_module, 'denoise')

                # At this point we assume the code ran successfully and we add it to the notebook:
                if self.notebook:
                    self.notebook.add_code_cell(code)

                # Run denoising:
                with asection(f"Running image denoising..."):
                    denoised_image = denoise(viewer)

                # Add to viewer:
                viewer.add_image(denoised_image, name='denoised')

                # Message:
                message = f"Success: image denoised and added to the viewer as layer 'denoised'. "

                aprint(f"Message: {message}")

                return message

        except Exception as e:
            traceback.print_exc()
            return f"Error: {type(e).__name__} with message: '{str(e)}' occured while trying to fulfill the request. " #\n```python\n{code}\n```\n



@cache
def install_aydin():
    with asection(f"Installing Aydin if not already present."):
        message = ''
        if platform.system() == 'Darwin':
            if 'arm64' in sys.platform.uname():
                aprint('Cannot install Aydin on M1/M2 macs!')
                raise NotImplementedError('Cannot install Aydin on M1/M2 macs!')

        message += pip_install(['aydin'])





