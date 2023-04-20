from langchain.tools import BaseTool

from napari_chatgpt.utils.google import search_overview

class GoogleSearchTool(BaseTool):
    name = "GoogleSearch"
    description = "Useful for when you need to answer questions by querying the web"

    def _run(self, query: str) -> str:
        """Use the tool."""
        result = search_overview(query=query)
        return result
    
    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("GoogleSearchTool does not support async")

