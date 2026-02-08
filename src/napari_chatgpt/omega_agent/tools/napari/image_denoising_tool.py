"""A tool for controlling a napari instance."""

import platform
import sys
import traceback
from functools import cache

from arbol import aprint, asection
from napari import Viewer

from napari_chatgpt.omega_agent.tools.base_napari_tool import (
    BaseNapariTool,
    _get_delegated_code,
)
from napari_chatgpt.utils.python.dynamic_import import dynamic_import
from napari_chatgpt.utils.python.pip_utils import pip_install

_image_denoising_prompt = """
**Context**
You write Python code to denoise images using a napari viewer.

**Task:**
Write a function `denoise(viewer) -> ArrayLike` that calls `aydin_classic_denoising()` or `aydin_fgr_denoising()`.
The napari viewer instance is available as `viewer`.

**ONLY AVAILABLE DENOISING FUNCTIONS:**
The only denoising functions you can use are `aydin_classic_denoising()` and `aydin_fgr_denoising()`:

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

- Answer in markdown with a single function `denoise(viewer) -> ArrayLike` that takes the viewer and returns the denoised image.

{last_generated_code}

**Viewer Information:**
{viewer_information}

**System Information:**
{system_information}

**Request:** 
{input}

**Answer in markdown:**
"""

_instructions = """

**Instructions specific to calling the denoising functions:**
- Call `aydin_classic_denoising()` or `aydin_fgr_denoising()` directly — they are already available in scope, do not redefine them.
- Use only these wrapper functions; do not call the Aydin API directly or use `skimage.restoration` or other denoising libraries.
- The system adds the result to the viewer automatically — do not call `viewer.add_image()`.
- Return only the function `denoise(viewer) -> ArrayLike`.
"""


class ImageDenoisingTool(BaseNapariTool):
    """
    A tool for denoising images using different algorithms.
    """

    def __init__(self, **kwargs):
        """
        Initialize the ImageDenoisingTool.

        Parameters
        ----------
        **kwargs: Additional keyword arguments to pass to the base class.
            This can include parameters like `notebook`, etc.
        """
        super().__init__(**kwargs)

        self.name = "ImageDenoisingTool"
        self.description = (
            "Use this tool when you need to denoise nD images. "
            "Input must be a plain text request that must mention 'Aydin's classic' or 'Aydin's FGR' approaches. "
            "For example, you can request to: 'denoise the image on the selected layer with Aydin's FGR approach', or 'denoise layer named `noisy` with Aydin's classic butterworth approach'. "
            "Aydin is a feature-rich and fast nD image denoising library. "
            "This tool operates on image layers present in the already instantiated napari viewer. "
        )
        self.prompt = _image_denoising_prompt
        self.instructions = _instructions
        self.save_last_generated_code = False

    # generic_codegen_instructions: str = ''

    def _run_code(self, request: str, code: str, viewer: Viewer) -> str:

        try:
            with asection(f"ImageDenoisingTool:"):
                with asection(f"Request:"):
                    aprint(request)
                aprint(f"Resulting in code of length: {len(code)}")

                # prepare code:
                code = super()._prepare_code(code)

                # lower case code:
                code_lower = code.lower()

                # Pick the right denoising code:
                if "aydin_classic_denoising(" in code_lower:
                    install_aydin()
                    if not _aydin_available():
                        return _AYDIN_MISSING_MSG
                    denoising_code = _get_delegated_code("aydin_classic")
                elif "aydin_fgr_denoising(" in code_lower:
                    install_aydin()
                    if not _aydin_available():
                        return _AYDIN_MISSING_MSG
                    denoising_code = _get_delegated_code("aydin_fgr")
                else:
                    raise ValueError(
                        f"Could not determine the denoising function used!"
                    )

                # combine generated code and functions:
                code = denoising_code + "\n\n" + code

                with asection(f"Code:"):
                    aprint(code)

                # Load the code as module:
                loaded_module = dynamic_import(code)

                # get the function:
                denoise_function = getattr(loaded_module, "denoise")

                # Run denoising:
                with asection(f"Running image denoising..."):
                    denoised_image = denoise_function(viewer)

                # Call the activity callback. At this point we assume the code is correct because it ran!
                self.callbacks.on_tool_activity(self, "coding", code=code)

                # Add to viewer:
                viewer.add_image(denoised_image, name="denoised")

                # Add call to denoise function & add to napari viewer:
                code += f"\n\ndenoised_image = denoise(viewer)"
                code += f"\nviewer.add_image(denoised_image, name='denoised')"

                # At this point we assume the code ran successfully and we add it to the notebook:
                if self.notebook:
                    self.notebook.add_code_cell(code)

                # Come up with a filename:
                filename = f"generated_code_{self.__class__.__name__}.py"

                # Add the snippet to the code snippet editor:
                from napari_chatgpt.microplugin.microplugin_window import (
                    MicroPluginMainWindow,
                )

                MicroPluginMainWindow.add_snippet(filename=filename, code=code)

                # Message:
                message = f"Success: image denoised and added to the viewer as layer 'denoised'. "

                aprint(f"Message: {message}")

                return message

        except Exception as e:
            traceback.print_exc()
            return f"Error: {type(e).__name__} with message: '{str(e)}' occurred while trying to fulfill the request. "  # \n```python\n{code}\n```\n


_AYDIN_MISSING_MSG = (
    "Error: The aydin denoising library could not "
    "be installed. "
    "Please install it manually: pip install aydin"
)


def _aydin_available() -> bool:
    """Check if the aydin package is importable."""
    import importlib.util

    return importlib.util.find_spec("aydin") is not None


@cache
def install_aydin():
    with asection(f"Installing Aydin if not already present."):
        message = ""
        if platform.system() == "Darwin":
            if "arm64" in platform.machine():
                aprint("Cannot install Aydin on M1/M2 macs!")
                raise NotImplementedError("Cannot install Aydin on M1/M2 macs!")

        message += pip_install(["aydin"])
