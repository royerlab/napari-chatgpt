from napari_chatgpt.tools.async_base_tool import AsyncBaseTool
from napari_chatgpt.utils.duckduckgo import search_overview


class WebSearchTool(AsyncBaseTool):
    name = "WebSearch"
    description = "Useful for when you need to answer questions by querying the web"

    def _run(self, query: str) -> str:
        """Use the tool."""
        result = search_overview(query=query)
        return result
