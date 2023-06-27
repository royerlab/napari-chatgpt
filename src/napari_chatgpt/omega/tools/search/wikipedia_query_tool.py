import traceback

from arbol import asection, aprint
from langchain import WikipediaAPIWrapper

from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool

_api_wrapper = WikipediaAPIWrapper()


class WikipediaQueryTool(AsyncBaseTool):
    """Tool that adds the capability to search using the Wikipedia API."""

    name = "WikipediaQueryTool"
    description = (
        "Use this tool to answer general questions on topics covered by an encyclopedia "
        "such as historical events, scientific concepts, geography... "
        "for which you don't already have the answer. "
        "Input must be a plain text wikipedia search query. "
        "Do NOT use this tool if you already have the answer."
    )

    def _run(self, query: str) -> str:
        """Use the Wikipedia tool."""
        try:
            with asection(f"WikipediaQueryTool: query= {query} "):
                # Run wikipedia query:
                result = _api_wrapper.run(query)

                with asection(f"Result:"):
                    aprint(result)

                return result

        except Exception as e:
            traceback.print_exc()
            return f"Error: {type(e).__name__} with message: '{str(e)}' occured while trying to query wikipedia for: '{query}'."
