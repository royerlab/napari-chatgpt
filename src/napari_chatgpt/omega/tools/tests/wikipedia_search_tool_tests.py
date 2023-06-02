from napari_chatgpt.omega.tools.search.wikipedia_search_tool import \
    WikipediaSearchTool


def test_wikipedia_search_tool():
    tool = WikipediaSearchTool()
    query = "Albert Einstein"
    result = tool._run(query)
    assert 'atlas' in result or 'zebrafish' in result or 'RNA' in result
