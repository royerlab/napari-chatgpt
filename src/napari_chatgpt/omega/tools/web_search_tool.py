from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool
from napari_chatgpt.utils.duckduckgo import summary_ddg


class WebSearchTool(AsyncBaseTool):
    name = "WebSearch"
    description = "Useful for when you need to answer questions by querying the web"

    def _run(self, query: str) -> str:
        """Use the tool."""
        result = summary_ddg(query=query)
        return result
