"""A tool for making a napari widget."""
import traceback

from arbol import asection, aprint
from napari import Viewer

from napari_chatgpt.omega.tools.napari.napari_base_tool import NapariBaseTool
from napari_chatgpt.utils.python.dynamic_import import dynamic_import
from napari_chatgpt.utils.strings.filter_lines import filter_lines
from napari_chatgpt.utils.strings.find_function_name import \
    find_magicgui_decorated_function_name
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

_instructions = \
"""

**Instructions for manipulating arrays from Image layers:**
- Convert arrays to the float type before processing if necessary.
- Any intermediate or locally created image array should also be of type float.
- The dtype of a RGB or RGBA image must be uint8 within the range [0, 255] to be viewable in napari.
- When creating image arrays using functions like np.full(), np.ones(), np.zeros(), etc., use float parameters (e.g., 1.0).
- Do NOT clip (np.clip) the resulting image unless explicitly instructed.

**Instructions for manipulating arrays from Label layers:**
- Do NOT convert arrays originating from label layers to float. Instead, cast them to np.uint32.

**Instructions for function parameters and magicgui decorator:**
- Accept integers, floats, booleans, or any other type that is compatible with the magicgui library.
- Decorate the function with the magicgui decorator: '@magicgui(call_button='Run')'. 
- Ideally, replace the call_button text 'Run' with a few short words that more explicit describe the action of the widget.
- Set 'result_widget=True' in the decorator, if and ONLY if, the widget function returns a string, or a *single* int, float, or a *short* list or tuple.
- Set 'result_widget=False' in the decorator, the most likely setting, if the widget function returns a numpy array, a napari data type *Data, or a napari layer.
- To expose a float parameter as a slider, include <parameter_name>={{"widget_type": "FloatSlider", 'min':<min_value>, 'max': <max_value>}} in the decorator.
- To expose a string parameter as dropdown choice, include <parameter_name>={{"choices": ['first', 'second', 'third']}}.
- Do NOT use tuples for widget function parameters.
- Do NOT expose *args and **kwargs as widget function parameters.
- Pay attention to the data types required by the library functions you use, for example: convert a float to an int before passing to a function that requires an int.

 **Instructions for using provided viewer instance:**
- Do NOT create a new instance of a napari viewer. Assume one is provided in the variable 'viewer'.
- Do NOT manually add the widget to the napari window by calling viewer.window.add_dock_widget().
- Do NOT use the viewer to add layers to the napari window within the function. Instead, use a return statement to return the result.

**Instructions for usage of delegated functions:**
- If you need to write and call an auxiliary function, then this auxiliary function MUST be defined within the widget function.

**Instructions on how to choose the function parameter types:**
- There are two mutually exclusive options for passing data:

    (i) The first kind of function signature should be typed with any of the following type hints:
        - napari layer data types: ImageData, LabelsData, PointsData, ShapesData, SurfaceData, TracksData, and VectorsData from 'napari.types'.
    
    (ii) The second kind of function signature should be typed with any of the following type hints:
        - napari layer types: Data, Labels, Points, Shapes, Surface, Tracks, and Vectors from 'napari.layers'.
 
- The function code must be consistent: if you use layers, access the data via 'layer.data'. Otherwise, you can directly operate on the arrays.
- Do not mix these two options for the function parameters.
- The function signature should include a type hint for the return value, such as '-> ImageData' or '-> Image'.

**Instructions for imports:**
- The following imports are already included in the code prefix that is prepended to the code you provide:
```python
from napari.types import ImageData, LabelsData, PointsData, ShapesData, SurfaceData, TracksData, VectorsData
from napari.layers import Image, Labels, Points, Shapes, Surface, Tracks, Vectors
```
- If you need to import other libraries, do so outside of the function.

"""

_code_prefix = """
from magicgui import magicgui
from napari.types import ImageData, LabelsData, PointsData, ShapesData, SurfaceData, TracksData, VectorsData
from napari.layers import Image, Labels, Points, Shapes, Surface, Tracks, Vectors
import numpy as np
from typing import Union
"""

_code_lines_to_filter_out = ['viewer = napari.Viewer(',
                               'viewer = Viewer('
                               'viewer.window.add_dock_widget(',
                               'napari.run(',
                               'viewer.add_image(',
                               'viewer.add_labels(',
                               'viewer.add_points(',
                               'viewer.add_shapes(',
                               'viewer.add_surface(',
                               'viewer.add_tracks(',
                               'viewer.add_vectors(',
                               'gui_qt(']

class NapariWidgetMakerTool(NapariBaseTool):
    """A tool for making napari widgets"""

    name = "NapariWidgetMakerTool"
    description = (
        "Use this tool to make a napari widget. "
        "Input must be a plain text description of the requested function and its parameters. "
        "The input must not assume knowledge of our conversation. "
        "For instance, if the input is for a 'Gaussian filter with a sigma parameter', "
        "this tool will make a napari widget that can apply a Gaussian filter to an image. "
        "Another example: if the input is to 'add a mean parameter to the previous widget', "
        "this tool will make a new version of the previosuly generated widget, but with mean parameter. "
        # "Another example: if the input is to 'remove the inexistent parameter num_cores from the Gaussian filter with a sigma parameter widget', "
        # "this tool will make a new version of the previously generated widget, but without the offending parameter. "
        "Important: The input must fully describe the widget every time, and in addition describe the modifications or fixes. "
        "This tool only makes widgets from function descriptions, "
        "it does not directly process or analyse images or other napari layers. "
        "Only use this tool when you need to make, modify, or fix a widget, not to answer questions! "
        "Do NOT include code in the input."
    )

    code_prefix = _code_prefix
    prompt = _napari_widget_maker_prompt
    instructions = _instructions
    save_last_generated_code = False
    return_direct: bool = True

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:

        try:

            with asection(f"NapariWidgetMakerTool: query= {query} "):

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

                    # Standalone code with the viewer.window.add_dock_widget call:
                    standalone_code = f"{code}\n\nviewer.window.add_dock_widget({function_name}, name='{function_name}')"

                    # At this point we assume the code ran successfully and we add it to the notebook:
                    if self.notebook:
                        self.notebook.add_code_cell(standalone_code)

                    # Add the snippet to the code snippet editor:
                    from microplugin.microplugin_window import MicroPluginMainWindow
                    MicroPluginMainWindow.add_snippet(filename=function_name, code=standalone_code)

                    message = f"The requested widget has been successfully created and registered to the viewer."

                # If the function does not exist:
                else:
                    message = f"Could not find a function for the requested widget."

                with asection(f"Message:"):
                    aprint(message)

                return message

        except Exception as e:
            traceback.print_exc()
            return f"Error: {type(e).__name__} with message: '{str(e)}' occured while trying to create the requested widget. " #with code:\n```python\n{code}\n```\n.

