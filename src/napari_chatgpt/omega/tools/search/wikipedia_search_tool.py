import traceback

from arbol import asection, aprint

from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool
from napari_chatgpt.utils.web.wikipedia import search_wikipedia


class WikipediaSearchTool(AsyncBaseTool):
    name = "WikipediaSearchTool"
    description = (
        "Use this tool to answer general questions on topics covered by an encyclopedia "
        "such as historical events, scientific concepts, geography... "
        "for which you don't already have the answer. "
        "Input must be a plain text wikipedia search query. "
        "Do NOT use this tool if you already have the answer.")

    def _run(self, query: str) -> str:
        """Use the tool."""
        try:

            with asection(f"WikipediaSearchTool: query= {query} "):
                # Run wikipedia search:
                result = search_wikipedia(query=query)

                with asection(f"Result:"):
                    aprint(result)

                return result

        except Exception as e:
            traceback.print_exc()
            return f"Error: {type(e).__name__} with message: '{str(e)}' occured while trying to search wikipedia for: '{query}'."
