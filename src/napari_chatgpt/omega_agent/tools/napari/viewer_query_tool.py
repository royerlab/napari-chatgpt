"""A tool for controlling a napari instance."""

import traceback
from contextlib import redirect_stdout
from io import StringIO

from arbol import asection, aprint
from napari import Viewer

from napari_chatgpt.omega_agent.tools.base_napari_tool import BaseNapariTool
from napari_chatgpt.utils.python.dynamic_import import dynamic_import

_napari_viewer_query_prompt = \
"""
**Context**
You are an expert python programmer with deep expertise in image processing and analysis.
You have perfect knowledge of the napari viewer's API.

**Task:**
Your task is to write Python code that can query an already instantiated napari viewer instance based on a plain text request. The code should be able to perform various operations such as returning information about the state of the viewer, the layers present, the dtype or shape of an image, and analyzing the content of different layers. For example, you can count the number of segments in a labels layer using the np.unique function, retrieve characteristics of individual segments like centroid coordinates, area/volume, or return statistics about the shape, area/volume, and positions of segments. You may also collect diverse measurements and statistics about segments in a labels layer.
To answer the request, you need to implement a Python function called `query(viewer)` which takes the napari viewer as a parameter and returns a string. This string will be the answer to the request.

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

_instructions = """
- Do **not** call the `query(viewer)` function yourself.
- Provide your answer **only** in Markdown format.

**Layer Reference Guidelines:**
- If the request mentions "this/that/the image (or layer)", assume it refers to the **last added layer**.
- If uncertain about which layer is meant, use the **last layer of the most appropriate type** for the request.
- If the request mentions the "selected image", use the **active or selected image layer**.
- To access the selected layer, use: `viewer.layers.selection.active`.

**Napari Viewer Usage:**
- The napari viewer instance is available as the variable `viewer`.
- You can directly access properties, e.g., `viewer.layers[0].data.shape`.
- **Do not** use `napari.Viewer()` or `gui_qt()` in your code.
- **Do not** create a new napari viewer instance; always use the provided `viewer`.
- Ensure all viewer API calls are correct and relevant to the request.
- Strive for accuracy in your response.

**Critical Instruction:**
- Implement a function `query(viewer) -> str` that takes the viewer as a parameter and returns the answer as a string.
"""


class NapariViewerQueryTool(BaseNapariTool):
    """
    A tool for querying the state of a napari viewer instance.
    """

    def __init__(self, **kwargs):
        """
        Initialize a tool for answering concise, plain-text queries about the state of a napari viewer and its layers.
        
        This constructor sets up the tool's metadata, prompt template, and usage instructions, configuring it to generate and execute code that inspects an existing napari viewer instance. The tool is intended for short, explicit queries and is not suitable for requests that would return large datasets.
        """
        super().__init__(**kwargs)

        self.name = "NapariViewerQueryTool"
        self.description = (
            "Use this tool when you need to a short answer to a question about the napari viewer, "
            "its state, or its layers (images, labels, points, tracks, shapes, and meshes). "
            "The input must be a plain text description of what you want to do, it should not contain code, it must not assume knowledge of our conversation, and it must be explicit about what is asked."
            "For instance, you can request to 'return the number of segments in the selected labels layer', 'return the total number of pixels/voxels in all image layers', or 'the number of unique colors' (selected layer is assumed by default). "
            "Important: this tool should not be used for requests that are expected to return large ampounts of data, entire files, large tables or arrays (>60 entries). "
            "For instance, do not use this tool to list pixels of an image, to return the coordinates of all points in a points layer, or to list segments in a labels layer. "
            "This tool returns a short answer to the request. "
        )
        self.prompt = _napari_viewer_query_prompt
        self.instructions = _instructions
        self.save_last_generated_code = False

    def _run_code(self, query: str, code: str, viewer: Viewer) -> str:

        """
        Dynamically executes generated Python code to answer a query about the state of a napari viewer.
        
        The method prepares and imports the provided code as a module, retrieves the `query(viewer)` function, and executes it with the given viewer instance. It captures any standard output produced during execution, logs relevant information, and integrates the code into a notebook and snippet editor if configured. Returns a formatted message containing the response and any captured output, or an error message if execution fails.
        
        Parameters:
            query (str): The plain-text query to be answered about the napari viewer.
            code (str): The dynamically generated Python code implementing the `query(viewer)` function.
            viewer (Viewer): The napari viewer instance to be queried.
        
        Returns:
            str: The response to the query, including any captured standard output or an error message if execution fails.
        """
        try:
            with asection(f"NapariViewerQueryTool:"):
                with asection(f"Query:"):
                    aprint(query)
                aprint(f"Resulting in code of length: {len(code)}")

                # prepare code:
                code = super()._prepare_code(code, do_fix_bad_calls=self.fix_bad_calls)

                # Load the code as module:
                loaded_module = dynamic_import(code)

                # get the function:
                query_function = getattr(loaded_module, "query")

                # Redirect output:
                f = StringIO()
                with redirect_stdout(f):
                    # Run query code:
                    response = query_function(viewer)

                    # Add call to query function and print response:
                    code += f"\n\nresponse = query(viewer)"
                    code += f"\n\nprint(response)"

                    # Add successfully run code to notebook:
                    if self.notebook:
                        self.notebook.add_code_cell(code + "\n\nquery(viewer)")

                    # Come up with a filename:
                    filename = f"generated_code_{self.__class__.__name__}.py"

                    # Add the snippet to the code snippet editor:
                    from napari_chatgpt.microplugin.microplugin_window import (
                        MicroPluginMainWindow,
                    )

                    MicroPluginMainWindow.add_snippet(filename=filename, code=code)

                # Get captured stdout:
                captured_output = f.getvalue()

                # Message:
                if len(captured_output) > 0:
                    message = f"Tool completed query successfully, here is the response:\n\n{response}\n\nand the captured standard output:\n\n{captured_output}\n\n"
                else:
                    message = f"Tool completed query successfully, here is the response:\n\n{response}\n\n"

                with asection(f"Message:"):
                    aprint(message)

                return message

        except Exception as e:
            traceback.print_exc()
            return f"Error: {type(e).__name__} with message: '{str(e)}' occurred while trying to query the napari viewer."  # with code:\n```python\n{code}\n```\n.
