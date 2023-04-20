from langchain import WikipediaAPIWrapper
from langchain.tools.wikipedia.tool import WikipediaQueryRun

from src.napari_chatgpt.tools.google_search_tool import GoogleSearchTool
from src.napari_chatgpt.tools.functions_info import PythonFunctionsInfoTool
from src.napari_chatgpt.tools.wikipedia_search_tool import WikipediaSearchTool


def test_tools():

    tool = PythonFunctionsInfoTool()

    query = "skimage.morphology.watershed"
    result = tool._run(query)
    assert len(result) < 300
    assert 'markers = None' in result

    query = "*skimage.morphology.watershed"
    result = tool._run(query)
    assert len(result) > 300
    assert 'markers' in result




