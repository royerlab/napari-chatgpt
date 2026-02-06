"""A tool for controlling a napari instance."""

import traceback

from arbol import aprint, asection
from napari import Viewer

from napari_chatgpt.omega_agent.tools.base_napari_tool import BaseNapariTool

_napari_viewer_control_prompt = """
**Context**
You write Python code to control a napari viewer instance for image processing and analysis tasks.
The viewer instance is accessible as `viewer`, so you can directly use methods like `viewer.add_image(np.zeros((10,10)))` without any preamble.

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

_instructions = r"""

**Instructions for controlling the napari viewer:**
- When adding images, labels, points, shapes, surfaces, tracks, or vectors, include code to load data from disk or download from a URL if needed.
- By default, create new layers for results; do not modify existing layers unless the request is explicit.
"""

_code_prefix = """
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
                aprint(f"Resulting in code of length: {len(code)}")

                # Prepare code:
                code = super()._prepare_code(code)

                captured_output = self._execute_code(code, viewer=viewer)

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
