from napari_chatgpt.omega_agent.tools.search.wikipedia_search_tool import (
    WikipediaSearchTool,
)


def test_wikipedia_search_tool():
    tool = WikipediaSearchTool()
    query = "Albert Einstein"
    result = tool.run_omega_tool(query)
    assert "atlas" in result or "zebrafish" in result or "RNA" in result
