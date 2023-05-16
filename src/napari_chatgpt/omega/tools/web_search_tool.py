from napari_chatgpt.omega.tools.machinery.async_base_tool import AsyncBaseTool
from napari_chatgpt.utils.web.duckduckgo import summary_ddg


class WebSearchTool(AsyncBaseTool):
    name = "WebSearch"
    description = "Useful for when you need to answer questions on current events, people, and any other topic that a web search would help with."

    def _run(self, query: str) -> str:
        """Use the tool."""
        result = summary_ddg(query=query)
        return result
