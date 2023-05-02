from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool
from napari_chatgpt.utils.wikipedia import search_wikipedia


class WikipediaSearchTool(AsyncBaseTool):
    name = "WikipediaSearch"
    description = "Useful for when you need to answer questions that might be " \
                  "contained in wikipedia's encyclopedic resource. "

    def _run(self, query: str) -> str:
        """Use the tool."""
        result = search_wikipedia(query=query)
        return result
