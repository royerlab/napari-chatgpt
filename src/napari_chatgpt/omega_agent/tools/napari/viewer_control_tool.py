"""A tool for controlling a napari instance."""

import traceback

from arbol import asection, aprint
from napari import Viewer

from napari_chatgpt.omega_agent.tools.base_napari_tool import BaseNapariTool

_napari_viewer_control_prompt =\
"""
**Context**
You are an expert python programmer strong coding skills and deep expertise in image processing and analysis.
You can solve all kinds of programming problems by writing high-quality python code.
You have perfect knowledge of the napari viewer's API.

**Task:**
Your task is to write Python code to control an already instantiated napari viewer instance based on a plain text request. 
The viewer instance is accessible using the variable `viewer`, so you can directly use methods like `viewer.add_image(np.zeros((10,10)))` without any preamble.

**Instructions:**
{instructions}

{last_generated_code}

**Viewer Information:**
{viewer_information}

**System Information:**
{system_information}

**Request:**
{input}

**Answer in markdown:**
"""

_instructions =\
"""

**Instructions for controlling the napari viewer:**
- When adding images, labels, points, shapes, surfaces, tracks, or vectors, include code to load data from disk or download from a URL if needed.
- By default, create new layers for results; do not modify existing layers unless the request is explicit.
- Convert image arrays to float type before processing when appropriate.
- Use float type for intermediate or local image arrays. For constants like `np.full()`, `np.ones()`, or `np.zeros()`, use floats (e.g., `1.0`).
- Output images should be float type, except for RGB images and label layers.
- RGB or RGBA images must be `uint8` in the range \[0, 255\] to display correctly in napari.
- If the request refers to "this," "that," or "the image/layer," assume it means the most recently added layer.
- If unsure which layer is referenced, use the last layer of the most relevant type for the request.
- If the request mentions the "selected image," use the active or selected image layer.
- Access the selected layer with: `viewer.layers.selection.active`
- Write only safe code that does not delete or damage files or the computer.
- Always end your code with a print statement that clearly summarizes what was (or was not) accomplished.
- Never create a new `napari.Viewer()` instance; always use the provided `viewer` variable.
- Double-check that all calls to viewer methods are correct and valid.
- Ensure your code is correct, robust, and ready to run.
"""

_code_prefix =\
"""
import napari
"""


class NapariViewerControlTool(BaseNapariTool):
    """
    A tool for controlling a napari viewer instance.
    """

    def __init__(self, **kwargs):
        """
        Initialize the NapariViewerControlTool.

        Parameters
        ----------
        kwargs: dict
            Additional keyword arguments to pass to the base
        """
        super().__init__(**kwargs)

        self.name = "NapariViewerControlTool"
        self.description = (
            "Use this tool when you want to control or adjust parameters or settings of the napari viewer, perform actions on its layers "
            "(images, labels, points, tracks, shapes, and meshes). "
            "This tool can perform any task that requires access to the viewer, its layers, and data contained in the layers. "
            "The input must be a plain text description of what you want to do, it should not contain code, it must not assume knowledge of our conversation, and it must be explicit about what is asked."
            "For instance, you can request to 'apply a Gaussian filter to the selected image', or 'max project the image layer `volume` along the 3rd dimension'. "
            "This tool returns a message that summarises what was done. "
        )
        self.prompt = _napari_viewer_control_prompt
        self.instructions = _instructions
        self.code_prefix = _code_prefix
        self.save_last_generated_code = False

    def _run_code(self, request: str, code: str, viewer: Viewer) -> str:

        try:
            with asection(f"NapariViewerControlTool:"):
                with asection(f"Request:"):
                    aprint(request)

                # Prepare code:
                code = super()._prepare_code(code, do_fix_bad_calls=self.fix_bad_calls)

                captured_output = self._run_code_catch_errors_fix_and_try_again(
                    code,
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
            return f"Error: {type(e).__name__} with message: '{str(e)}' occurred while fulfilling request. "  # \n```python\n{code}\n```\n
