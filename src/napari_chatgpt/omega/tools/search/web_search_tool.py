from arbol import asection, aprint

from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool
from napari_chatgpt.utils.web.metasearch import metasearch


class WebSearchTool(AsyncBaseTool):
    name = "WebSearch"
    description = (
        "Use this tool to answer questions for which you don't have the answer. "
        "Input must be a plain text web search query. "
        "For example, if the input is: 'What year is it?', the tool will return information about this question."
        "Use it sparingly and refrain from using it if you already know the answer!")

    def _run(query: str, self) -> str:
        """Use the tool."""

        with asection(f"WebSearchTool: query= {query} "):
            # Run metasearch query:
            result = metasearch(query=query)

            with asection(f"Search result:"):
                aprint(result)

            return result
