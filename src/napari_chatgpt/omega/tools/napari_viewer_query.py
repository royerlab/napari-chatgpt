"""A tool for controlling a napari instance."""

from napari import Viewer

from napari_chatgpt.omega.tools.napari_base_tool import NapariBaseTool
from napari_chatgpt.utils.dynamic_import import dynamic_import

_napari_viewer_query_prompt = """
"
Task:
Given a plain text request, you competently write python code to query an already instantiated napari viewer instance.

You can, for example: 

- count the number of segments of a labels layer by using the function: np.unique.
- return the centroid coordinates, area/volume, or other characteristics of individual segments.
- return statistics about the shape, area/volume, and positions of segments.
- collect diverse measurements and statistics about segments in a labels layer.
- return information about the dtype or shape of an image

You answer requests by implementing a python function: query(viewer)->str which takes the napari viewer and returns a string.
The returned string is the answer to the request. 

Notes about which layer is meant:
- If the request mentions 'this/that/the image (or layer)' then most likely it refers to the last added layer.
- If you are not sure what layer is referred to, assume it is the last layer of appropriate type to the request.

NAPARI VIEWER INSTRUCTIONS: 
- The napari viewer instance is immediately available by using the variable: 'viewer'. 
- For example, you can directly write: viewer.layers[0].data.shape without preamble. 
- Therefore, DO NOT use 'napari.Viewer()' or 'gui_qt():' in your code. 
- DO NOT CREATE A NEW INSTANCE OF A NAPARI VIEWER, use the one provided in the variable: 'viewer'.
- Make sure the calls to the viewer are correct.

{generic_codegen_instructions}
 
Request:
{input}

Answer in markdown with a single function query(viewer)->str that takes the viewer and returns the response.
"""


class NapariViewerQueryTool(NapariBaseTool):
    """A tool for running python code in a REPL."""

    name = "NapariViewerQueryTool"
    description = (
        "Forward plain text requests to this tool when you need information about images, "
        "labels, points, tracks, shapes, meshes, etc... held by the napari viewer. "
        "Requests must be a plain text description (no code) of the request."
    )
    prompt = _napari_viewer_query_prompt

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:
        # prepare code:
        code = super()._prepare_code(code)

        # Load the code as module:
        loaded_module = dynamic_import(code)

        # get the function:
        query = getattr(loaded_module, 'query')

        # Run segmentation:
        response = query(viewer)

        return f"Success: answer to request:\n{response}"
