from langchain.tools import BaseTool

from napari_chatgpt.utils.wikipedia import search_wikipedia


class WikipediaSearchTool(BaseTool):
    name = "WikipediaSearch"
    description = "Useful for when you need to answer questions that might be" \
                  "contained in wikipedia's encyclopedic resource. " \
                  "If you prefix your request with a star character '*' "


    def _run(self, query: str) -> str:
        """Use the tool."""
        result = search_wikipedia(query=query)
        return result
    
    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("WikipediaSearchTool does not support async")

