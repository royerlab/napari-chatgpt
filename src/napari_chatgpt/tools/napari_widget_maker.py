"""A tool for running python code in a REPL."""
from typing import Callable

from napari import Viewer

from napari_chatgpt.utils.dynamic_import import dynamic_import
from napari_chatgpt.utils.filter_lines import filter_lines
from napari_chatgpt.utils.find_function_name import find_function_name
from napari_chatgpt.tools.napari_base_tool import NapariBaseTool

_prompt = """
Task:
You competently write image processing and image analysis functions in python given a plain text request. 
The function should be pure, self-contained, effective, well-written, syntactically correct.
The function should work on 2D and 3D images, and images of any number of dimensions (nD), 
unless the request is explicit about the number of dimensions. 
The function MUST convert all input image arrays to float type before processing. 
The function should not clip the resulting image unless input image(s) have been normalised accordingly.
The function should do all and everything that is asked, but nothing superfluous.

Instructions for Function Signature:
The function signature must be typed with any of the following type hints:
(i) napari layer data types: ImageData, LabelsData, PointsData, ShapesData, 
SurfaceData, TracksData, VectorsData. These types must be imported with import 
statements such as: 'from napari.types import ImageData' 
(ii) integers, floats, boolean, or any other type accepted by the magicgui library.
Decorate the function with the magicgui decorator: '@magicgui(call_button='Run')'
where <function_name> is the name of the function that you wrote.
DO NOT CREATE A NEW INSTANCE OF A NAPARI VIEWER, use the one provided in the variable: 'viewer'.
DO NOT write code to add the widget to the napari window by calling viewer.window.add_dock_widget().

{generic_codegen_instructions}

Request:  
{input}

Answer in pure python code:
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

from napari.types import ImageData

class NapariWidgetMakerTool(NapariBaseTool):
    """A tool for making napari widgets"""

    name = "NapariWidgetMakerTool"
    description = (
        "Forward to this tool requests to make napari function widgets from function descriptions. "
        "Requests must be a plain text description (no code) of an image processing or analysis function"
        "This tool will interpret the request and creates a napari function widget for it."
        "For example, you can ask for 'a gaussian filter widget with sigma parameter'. "
    )
    code_prefix = _code_prefix
    prompt = _prompt

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:

        # Extracts function name:
        function_name = find_function_name(code)

        # If the function exists:
        if function_name:

            # Remove any viewer add_dock_widget code:
            code = filter_lines(code, ['viewer.window.add_dock_widget('])

            # Load the code as module:
            module = dynamic_import(code)

            # get the function:
            function = getattr(module, function_name)

            # Load the widget in the viewer:
            viewer.window.add_dock_widget(function)

            return "Success: widget was created and registered to the viewer."

        else:
            return "Failure: function could not be found in provided code."