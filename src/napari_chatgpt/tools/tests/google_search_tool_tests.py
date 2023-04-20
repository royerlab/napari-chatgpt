from src.napari_chatgpt.tools.google_search_tool import GoogleSearchTool

def test_google_search_tool():

    tool = GoogleSearchTool()
    query = "What is zebrahub? "
    result = tool._run(query)
    assert 'atlas' in result or 'zebrafish' in result or 'RNA' in result

