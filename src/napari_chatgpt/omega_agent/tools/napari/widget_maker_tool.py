"""A tool for making a napari widget."""

import traceback

from arbol import aprint, asection
from napari import Viewer

from napari_chatgpt.omega_agent.tools.base_napari_tool import BaseNapariTool
from napari_chatgpt.utils.python.dynamic_import import dynamic_import
from napari_chatgpt.utils.strings.filter_lines import filter_lines
from napari_chatgpt.utils.strings.find_function_name import (
    find_magicgui_decorated_function_name,
)
from napari_chatgpt.utils.strings.trailing_code import remove_trailing_code

_napari_widget_maker_prompt = """
**Context**
You are an expert python programmer with deep expertise in image processing and analysis.

**Task:**
Your task is to competently write image processing and image analysis functions in Python based on a plain text request. The functions should meet the following criteria:
- The functions should be pure, self-contained, effective, well-written, and syntactically correct.
- The functions should work on 2D and 3D images, and ideally on images of any number of dimensions (nD), unless the request explicitly specifies the number of dimensions.
- The functions should perform all the required tasks precisely as requested, without adding any extra or unnecessary functionality.

**Instructions:**
{instructions}

- Make sure that the code is correct! 
{last_generated_code}

**Viewer Information:**
{viewer_information}

**System Information:**
{system_information}

**Request:**
{input}

**Answer in markdown:**
"""
#
# Important: all import statements must be inside of the function except for those needed for magicgui and for type hints.
# All import statements required by function calls within the function must be within the function.

_instructions = """

## 📌 Preamble  
*These instructions tell you how to write **one** napari + magicgui widget (function or class) that can be pasted directly into a Python cell. The caller will take care of docking the widget and launching napari.*

---

**General Rules**
- Emit **only code** (plus minimal docstrings if helpful). No extra prose, comments, or examples.
- Write **exactly one** widget.  If helper functions are needed, define them *inside* the main widget.
- **Never** create or show a new `napari.Viewer()`; a `viewer` variable will be supplied when required.
- Avoid side-effects (prints, file I/O, logging) unless explicitly asked.

---

**Instructions for manipulating arrays from Image layers:**
- Convert image data to `np.float32` before processing if necessary (`arr.astype(np.float32, copy=False)`).
- Intermediate arrays you create should also be `float32`.
- RGB/RGBA image arrays **must** be `uint8` in the 0-255 range to render correctly.
- When creating arrays with `np.ones`, `np.zeros`, `np.full`, etc., pass float literals (`1.0`, `0.0`).
- **Do not** clip (`np.clip`) or rescale results unless the user explicitly instructs.

---

**Instructions for manipulating arrays from Label layers:**
- Keep label data integer. Cast with `arr.astype(np.uint32, copy=False)` if needed.
- **Never** convert labels to float.

---

**Instructions for function parameters and `@magicgui` decorator:**
- Decorate the widget function with `@magicgui(call_button='<action>')`; replace `<action>` with a concise verb phrase (e.g. `"Apply Threshold"`).
- Use `result_widget=True` **only** if the return value is a small scalar, short string, or small tuple/list. Otherwise leave it `False`.
- To expose a float as a slider:  
  `some_float={"widget_type":"FloatSlider", "min":0.0, "max":1.0}` (adjust range as needed).
- To expose a string parameter as a dropdown:  
  `choice={"choices":["first","second","third"]}`.
- Do **not** use tuples, `*args`, or `**kwargs` as parameters.
- Put layer/data parameters **first** so they appear at the top of the widget UI.

---

**Instructions for returned images and/or layers:**
- Return **exactly one** of the following:
  1. **NumPy array** typed as `<LayerType>Data` (`ImageData`, `LabelsData`, …). napari will create a new layer automatically.  
  2. **Concrete napari `Layer` instance** (`Image`, `Labels`, `Points`, …).  
  3. **`napari.types.LayerDataTuple`** (or a *list* of tuples) for full control over data, metadata, and layer type.

- **Dtype & range rules**  
  * Images: `float32`/`float64` in 0-1 **or** `uint8` in 0-255 (RGB/A).  
  * Labels: keep `uint32`.

- **Updating an existing layer**  
  Include `metadata["name"]` in your `LayerDataTuple` and set it to the name of the layer you wish to update.

- **Never** call `viewer.add_*` or `viewer.window.add_dock_widget()`; relying on the return value avoids duplicates.

---

**Instructions for using the provided `viewer` instance:**
- Do **not** create a new viewer; use the injected `viewer` only if needed for read-only tasks.
- If the widget does not need the viewer, omit it from the signature.

---

**Instructions for helper / delegated functions:**
- Define helper functions **inside** the main widget function.
- Don’t close over large arrays; pass them as arguments.

---

**Instructions on how to choose function parameter type hints:**
Choose **one** style and use it consistently within the function:

| Style | Parameter hints | How you access data |
|-------|-----------------|----------------------|
| *Array-oriented* | `<LayerType>Data` (`ImageData`, `LabelsData`, …) | Operate on the NumPy array directly. |
| *Layer-oriented* | Concrete `Layer` classes (`Image`, `Labels`, …) | Access data via `layer.data`. |

*Do **not** mix these two styles in one function. The return type must follow the same convention.*

---

**Imports (already provided by the framework):**
```python
from napari.types import (
    ImageData, LabelsData, PointsData, ShapesData,
    SurfaceData, TracksData, VectorsData
)
from napari.layers import (
    Image, Labels, Points, Shapes, Surface, Tracks, Vectors
)
import numpy as np
from magicgui import magicgui
# Import any additional third-party libraries you need (e.g., skimage, scipy).

"""

_code_prefix = """
from magicgui import magicgui
from napari.types import ImageData, LabelsData, PointsData, ShapesData, SurfaceData, TracksData, VectorsData
from napari.layers import Image, Labels, Points, Shapes, Surface, Tracks, Vectors
import numpy as np
from typing import Union
"""

_code_lines_to_filter_out = [
    "viewer = napari.Viewer(",
    "viewer = Viewer(",
    "viewer.window.add_dock_widget(",
    "napari.run(",
    "viewer.add_image(",
    "viewer.add_labels(",
    "viewer.add_points(",
    "viewer.add_shapes(",
    "viewer.add_surface(",
    "viewer.add_tracks(",
    "viewer.add_vectors(",
    "gui_qt(",
]


class NapariWidgetMakerTool(BaseNapariTool):
    """
    A tool for making napari widgets
    """

    def __init__(self, **kwargs):
        """
        Initialize the NapariWidgetMakerTool.

        Parameters
        ----------
        **kwargs: dict
            Additional keyword arguments to pass to the base class.
            This can include parameters like `notebook`, `fix_bad_calls`, etc.
        """
        super().__init__(**kwargs)

        self.name = "NapariWidgetMakerTool"
        self.description = (
            "Use this tool to make a napari widget. "
            "Input must be a plain text description of the requested function and its parameters. "
            "The input must not assume knowledge of our conversation. "
            "For instance, if the input is for a 'Gaussian filter with a sigma parameter', "
            "this tool will make a napari widget that can apply a Gaussian filter to an image. "
            "Another example: if the input is to 'add a mean parameter to the previous widget', "
            "this tool will make a new version of the previously generated widget, but with mean parameter. "
            # "Another example: if the input is to 'remove the inexistent parameter num_cores from the Gaussian filter with a sigma parameter widget', "
            # "this tool will make a new version of the previously generated widget, but without the offending parameter. "
            "Important: The input must fully describe the widget every time, and in addition describe the modifications or fixes. "
            "This tool only makes widgets from function descriptions, "
            "it does not directly process or analyse images or other napari layers. "
            "Only use this tool when you need to make, modify, or fix a widget, not to answer questions! "
            "Do NOT include code in the input."
        )

        self.code_prefix = _code_prefix
        self.prompt = _napari_widget_maker_prompt
        self.instructions = _instructions
        self.save_last_generated_code = False
        self.return_direct: bool = True

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:

        try:

            with asection(f"NapariWidgetMakerTool: "):
                with asection(f"Query:"):
                    aprint(query)
                aprint(f"Resulting in code of length: {len(code)}")

                # Prepare code:
                code = super()._prepare_code(code, do_fix_bad_calls=self.fix_bad_calls)

                # Extracts function name:
                function_name = find_magicgui_decorated_function_name(code)

                # If the function exists:
                if function_name:

                    # Remove any viewer forbidden code:
                    code = filter_lines(code, _code_lines_to_filter_out)

                    # Remove trailing code:
                    code = remove_trailing_code(code)

                    # Load the code as module:
                    loaded_module = dynamic_import(code)

                    # get the function:
                    function = getattr(loaded_module, function_name)

                    # Load the widget in the viewer:
                    viewer.window.add_dock_widget(function, name=function_name)

                    # Call the activity callback. At this point we assume the code is correct because it ran!
                    self.callbacks.on_tool_activity(self, "coding", code=code)

                    # Standalone code with the viewer.window.add_dock_widget call:
                    standalone_code = f"{code}\n\nviewer.window.add_dock_widget({function_name}, name='{function_name}')"

                    # At this point we assume the code ran successfully and we add it to the notebook:
                    if self.notebook:
                        self.notebook.add_code_cell(standalone_code)

                    # Add the snippet to the code snippet editor:
                    from napari_chatgpt.microplugin.microplugin_window import (
                        MicroPluginMainWindow,
                    )

                    MicroPluginMainWindow.add_snippet(
                        filename=function_name, code=standalone_code
                    )

                    message = f"The requested widget has been successfully created and registered to the viewer."

                # If the function does not exist:
                else:
                    message = f"Could not find a function for the requested widget."

                with asection(f"Message:"):
                    aprint(message)

                return message

        except Exception as e:
            traceback.print_exc()
            return f"Error: {type(e).__name__} with message: '{str(e)}' occurred while trying to create the requested widget. "  # with code:\n```python\n{code}\n```\n.
