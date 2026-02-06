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
You write image processing and analysis functions as napari widgets using magicgui.
Functions should work on 2D and 3D images (and ideally nD) unless the request specifies otherwise.

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
#
# Important: all import statements must be inside of the function except for those needed for magicgui and for type hints.
# All import statements required by function calls within the function must be within the function.

_instructions = """

## Preamble
Write **one** napari + magicgui widget function. The caller handles docking the widget and launching napari.

---

**General Rules**
- Emit **only code** (plus minimal docstrings if helpful). No extra prose or examples.
- Write **exactly one** widget. Define helper functions *inside* the main widget if needed.
- Avoid side-effects (prints, file I/O, logging) unless explicitly asked.

---

**Labels Arrays:**
- Keep label data integer. Cast with `arr.astype(np.uint32, copy=False)` if needed.
- **Never** convert labels to float.

---

**`@magicgui` Decorator:**
- Decorate with `@magicgui(call_button='<action>')` using a concise verb phrase (e.g. `"Apply Threshold"`).
- Use `result_widget=True` **only** for small scalar/string/tuple return values.
- Float slider: `some_float={"widget_type":"FloatSlider", "min":0.0, "max":1.0}`.
- Dropdown: `choice={"choices":["first","second","third"]}`.
- Do **not** use tuples, `*args`, or `**kwargs` as parameters.
- Put layer/data parameters **first** in the signature.

---

**Return Values:**
- Return **exactly one** of:
  1. NumPy array typed as `<LayerType>Data` (`ImageData`, `LabelsData`, etc.).
  2. Concrete napari `Layer` instance (`Image`, `Labels`, `Points`, etc.).
  3. `napari.types.LayerDataTuple` (or a list of tuples).

- To update an existing layer, include `metadata["name"]` in your `LayerDataTuple`.
- **Never** call `viewer.add_*` or `viewer.window.add_dock_widget()`; use the return value instead.

---

**Viewer Usage:**
- If the widget needs the viewer, use the injected `viewer` for read-only tasks only.
- If the widget does not need the viewer, omit it from the signature.

---

**Type Hint Style:**
Choose **one** style consistently:

| Style | Parameter hints | Data access |
|-------|-----------------|-------------|
| *Array-oriented* | `ImageData`, `LabelsData`, etc. | Operate on the NumPy array directly. |
| *Layer-oriented* | `Image`, `Labels`, etc. | Access data via `layer.data`. |

Do **not** mix styles in one function.

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
            This can include parameters like `notebook`, etc.
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
                code = super()._prepare_code(code)

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
