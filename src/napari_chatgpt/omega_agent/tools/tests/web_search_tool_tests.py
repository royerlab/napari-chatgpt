from pprint import pprint

from napari_chatgpt.omega_agent.tools.search.web_search_tool import WebSearchTool


def test_web_search_tool():
    tool = WebSearchTool()
    query = "What is zebrahub?"
    result = tool.run_omega_tool(query)
    pprint(result)
    assert "atlas" in result or "zebrafish" in result or "RNA" in result
