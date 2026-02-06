"""A tool for controlling a napari instance."""

import traceback

from arbol import aprint, asection
from napari import Viewer

from napari_chatgpt.omega_agent.tools.base_napari_tool import BaseNapariTool

_napari_viewer_execution_prompt = """
**Context**
You are an expert python programmer with deep expertise in image processing and analysis.
You have perfect knowledge of the napari viewer's API.

**Task:**
Your task is to write arbitrary safe Python code that uses an already instantiated napari viewer instance based on a plain text request. 
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


_instructions = r"""

**Instructions for executing code with the napari viewer:**
- When adding images, labels, points, shapes, surfaces, tracks, or vectors, include code to load data from disk or a URL if needed.
- By default, create new layers for results; do not modify existing layers unless the request explicitly says so.
- Convert image arrays to float type before processing when appropriate.
- Use float type for intermediate or local image arrays. For constants like `np.full()`, `np.ones()`, or `np.zeros()`, use floats (e.g., 1.0).
- Output images should be float type, except for RGB images and label layers.
- RGB or RGBA images must be `uint8` in the \[0, 255\] range to display correctly in napari.
- If the request refers to "this," "that," or "the image/layer," assume it means the last added image/layer.
- If unsure which layer is referenced, use the last layer of the most relevant type.
- If the request mentions the "selected image," use the active or selected image layer.
- Access the selected layer with: `viewer.layers.selection.active`
- If saving a file and no path or filename is given, use the system desktop and a default filename.
- Only write safe code; never delete files or perform destructive actions.
- Always end your code with a print statement summarizing what was (or was not) achieved.
- Never create a new `napari.Viewer()` instance; always use the provided `viewer` variable.
- Double-check that all viewer method calls are correct.
- Ensure your code is correct, robust, and ready to run.
"""

_code_prefix = """
import napari
"""


class NapariViewerExecutionTool(BaseNapariTool):
    """
    A tool for executing arbitrary code that interacts with a napari viewer instance.
    """

    def __init__(self, **kwargs):
        """
        Initialize the NapariViewerExecutionTool.
        Parameters
        ----------
        **kwargs: dict
            Additional keyword arguments to pass to the base class.
            This can include parameters like `notebook`, `fix_bad_calls`, etc.
        """
        super().__init__(**kwargs)
        self.name = "NapariViewerExecutionTool"
        self.description = (
            "Use this tool when you need to perform tasks that require access to the napari viewer instance and its layers. "
            "This tool can perform any task that requires access to the viewer, its layers, and data contained in the layers. "
            "The input must be a plain text description of what you want to do, it should not contain code, it must not assume knowledge of our conversation, and it must be explicit about what is asked."
            "For example, you can ask to 'save the selected image to a file', or 'write in a CSV file on the desktop the list of segments in layer `segmented` ', or 'open file <filename> with the system viewer'. "
            "This tool returns a message that summarises what was done. "
        )
        self.prompt = _napari_viewer_execution_prompt
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
