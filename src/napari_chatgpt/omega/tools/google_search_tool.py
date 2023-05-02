from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool
from napari_chatgpt.utils.google import search_overview


class GoogleSearchTool(AsyncBaseTool):
    name = "GoogleSearch"
    description = "Useful for when you need to answer questions by querying the web."

    def _run(self, query: str) -> str:
        """Use the tool."""
        result = search_overview(query=query)
        return result
