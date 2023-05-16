from langchain import WikipediaAPIWrapper

from napari_chatgpt.omega.tools.machinery.async_base_tool import AsyncBaseTool

_api_wrapper = WikipediaAPIWrapper()


class WikipediaQueryTool(AsyncBaseTool):
    """Tool that adds the capability to search using the Wikipedia API."""

    name = "WikipediaQueryTool"
    description = (
        "Useful for when you need to answer general questions on topics covered by an encyclopedia such as historical events, scientific concepts, geography, etc... "
        "Input should be a search query."
    )

    def _run(self, query: str) -> str:
        """Use the Wikipedia tool."""
        return _api_wrapper.run(query)
