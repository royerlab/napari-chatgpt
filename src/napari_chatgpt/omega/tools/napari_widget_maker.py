"""A tool for making a napari widget."""

from napari import Viewer

from napari_chatgpt.omega.tools.napari_base_tool import NapariBaseTool
from napari_chatgpt.utils.dynamic_import import dynamic_import
from napari_chatgpt.utils.filter_lines import filter_lines
from napari_chatgpt.utils.find_function_name import find_function_name

_napari_widget_maker_prompt = """
Task:
You competently write image processing and image analysis functions in python given a plain text request. 
The function should be pure, self-contained, effective, well-written, syntactically correct.
The function should work on 2D and 3D images, and images of any number of dimensions (nD), 
unless the request is explicit about the number of dimensions. 
The widget should do all and everything that is asked, but nothing else or superfluous.

Instructions for manipulating arrays from Images layers:
- Convert arrays to float type before processing.
- Any intermediate or locally created image array should also be of type float.
- Images arrays created with: np.full(), np.ones(), np.zeros(), ... should use float parameters (for example 1.0).
- DO NOT clip (np.clip) the resulting image.

Instructions for manipulating arrays from Labels layers:
- DO NOT convert to float arrays originating from labels layers, instead cast to np.uint32.

Instructions for Function Signature:
- Integers, floats, boolean, or any other type accepted by the magicgui library.
- Decorate the function with the magicgui decorator: '@magicgui(call_button='Run')' where <function_name> is the name of the function that you wrote.
- DO NOT CREATE A NEW INSTANCE OF A NAPARI VIEWER, use the one provided in the variable: 'viewer'.
- DO NOT write code to add the widget to the napari window by calling viewer.window.add_dock_widget().

You have two mutually exclusive options for passing data:

    (i) The first kind of function signature must be typed with any of the following type hints:
    napari layer data types: ImageData, LabelsData, PointsData, ShapesData, 
    SurfaceData, TracksData, VectorsData. These types must be imported with import 
    statements such as: 'from napari.types import ImageData' 
    
    (ii) The second type of function signature must be typed with any of the following type hints:
    napari layer types: Data, Labels, Points, Shapes, Surface, Tracks, Vectors. 
    These types must be imported with import statements such as: 'from napari.layers import Image' 
    
The function code must be consistent: if you use layers then you access the data via: 'layer.data', otherwise you can directly operate on the arrays.
Do not mix these two options for the function parameters.
The function signature should have a type hint for the return, e.g.  -> ImageData or -> Image

{generic_codegen_instructions}

Request:  
{input}

Answer in markdown:
"""
#
# Important: all import statements must be inside of the function except for those needed for magicgui and for type hints.
# All import statements required by function calls within the function must be within the function.


_code_prefix = """
from magicgui import magicgui
from napari.types import ImageData, LabelsData, PointsData, ShapesData, SurfaceData, TracksData, VectorsData
import numpy as np
from typing import Union
"""


class NapariWidgetMakerTool(NapariBaseTool):
    """A tool for making napari widgets"""

    name = "NapariWidgetMakerTool"
    description = (
        "Forward plain text requests to this tool when you need to make napari function widgets from function descriptions. "
        "Requests must be a plain text description (no code) of an image processing or analysis function. "
        "For example, you can ask for 'a gaussian filter widget with sigma parameter'. "
        "This tool does not process or analyse images, it makes widget that then do that. "
        "ONLY use this tool when the word 'widget' is mentioned. "
    )
    code_prefix = _code_prefix
    prompt = _napari_widget_maker_prompt

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:

        code = super()._prepare_code(code)

        # Extracts function name:
        function_name = find_function_name(code)

        # If the function exists:
        if function_name:

            # Remove any viewer add_dock_widget code:
            code = filter_lines(code, ['viewer.window.add_dock_widget('])

            # Load the code as module:
            loaded_module = dynamic_import(code)

            # get the function:
            function = getattr(loaded_module, function_name)

            # Load the widget in the viewer:
            viewer.window.add_dock_widget(function)

            return "Success: widget was created and registered to the viewer."

        else:
            return "Failure: function could not be found in provided code."
