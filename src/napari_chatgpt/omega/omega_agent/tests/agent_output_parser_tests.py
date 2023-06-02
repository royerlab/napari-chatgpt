from langchain.schema import AgentAction, AgentFinish

from napari_chatgpt.omega.omega_agent.agent_output_parser import \
    OmegaAgentOutputParser

__tool_names = ['WikipediaTool', 'NapariWidgetMakerTool', 'NapariViewerControlTool']

__omega_agent_output_example_1 = \
"""
WikipediaTool: Albert Einstein
"""

__omega_agent_output_example_2 = \
"""
FinalAnswer: Hello! How can I assist you today?
"""

__omega_agent_output_example_3 = \
"""
NapariWidgetMakerTool: Please use the following plain text request to create a widget for edge detection in an image where the threshold is set to the minimum value:

`create an edge detection widget for an image where the threshold is set to the minimum value`

This will generate a widget that takes in an image and sets the threshold to the minimum value. The widget will then perform edge detection on the image using a 3x3 kernel and return the resulting edges as a new image.

Here is the code that was generated:
## Edge Detection Widget for Image

```python
import numpy as np
from scipy.signal import convolve2d
from napari.types import ImageData
from napari.layers import Image
from magicgui import magicgui


@magicgui(call_button='Detect Edges', result_widget=False)
def detect_edges(image: ImageData, threshold: float = None) -> ImageData:
    kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
    edges = convolve2d(image.astype(float), kernel, mode='same')
    if threshold is None:
        threshold = np.min(edges)
    edges = np.clip(edges, 0, threshold)
    return edges


viewer.window.add_dock_widget(detect_edges)
```

This code creates a widget that takes in an image and a threshold value. It uses a 3x3 kernel to perform edge detection on the image using the `convolve2d` function from `scipy.signal`. The resulting edges are then clipped to the threshold value and returned as a new image. If the threshold value is not provided, it is set to the minimum value of the edges. The widget is added to the napari viewer using `viewer.window.add_dock_widget`.
"""

__omega_agent_output_example_4 = \
"""
I apologize for the error. It seems there was an issue with adding the text layer. Let me try again.
NapariViewerControlTool: Add a text layer, slightly larger than the current image, so that Loic A. Royer can sign this work of digital art. Place the signature in the lower right corner, ensuring it does not overlap with the art itself. Set the text size to no more than 16 pixels relative to the dimensions of the image layer. Make sure to use the correct attribute to get the image dimensions.
"""

__omega_agent_output_example_5 = \
"""
Task has been completed! 
"""

def test_omega_agent_output_parser_action():
    parser = OmegaAgentOutputParser(tool_names=__tool_names)
    result = parser.parse(__omega_agent_output_example_1)
    print(result)
    assert isinstance(result, AgentAction)
    assert result.tool == 'WikipediaTool'
    assert result.tool_input == 'Albert Einstein'


def test_omega_agent_output_parser_final_answer():
    parser = OmegaAgentOutputParser(tool_names=__tool_names)
    result = parser.parse(__omega_agent_output_example_2)
    print(result)
    assert isinstance(result, AgentFinish)
    assert result.return_values['output'] == 'Hello! How can I assist you today?'


def test_omega_agent_output_parser_complex():
    parser = OmegaAgentOutputParser(tool_names=__tool_names)
    result = parser.parse(__omega_agent_output_example_3)
    print(result)
    assert isinstance(result, AgentAction)
    assert result.tool == 'NapariWidgetMakerTool'
    assert len(result.tool_input) > 400

def test_omega_agent_output_parser_comment_first():
    parser = OmegaAgentOutputParser(tool_names=__tool_names)
    result = parser.parse(__omega_agent_output_example_4)
    print(result)
    assert isinstance(result, AgentAction)
    assert result.tool == 'NapariViewerControlTool'
    assert 'Add a text layer' in result.tool_input
    assert 'I apologize for the error.' not in result.tool_input

def test_omega_agent_output_parser_direct_answer():
    parser = OmegaAgentOutputParser(tool_names=__tool_names)
    result = parser.parse(__omega_agent_output_example_5)
    print(result)
    assert isinstance(result, AgentFinish)
    assert len(result.return_values['output']) > 0
    assert 'Task has been completed!' in result.return_values['output']