import traceback

from arbol import aprint, asection

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool
from napari_chatgpt.utils.web.metasearch import metasearch


class WebSearchTool(BaseOmegaTool):
    """
    A tool for searching the web for information.
    This tool can be used to find answers to questions or gather information on various topics.
    """

    def __init__(self, **kwargs):
        """
        Initialize the WebSearchTool.

        Parameters
        ----------
        kwargs: dict
            Additional keyword arguments to pass to the base class.
            This can include parameters like `notebook`, `fix_bad_calls`, etc.
        """
        super().__init__(**kwargs)

        # Tool name and description:
        self.name = "WebSearch"
        self.description = (
            "Use this tool to answer questions for which you don't have the answer. "
            "Input must be a plain text web search query. "
            "For example, if the input is: 'What year is it?', the tool will return information about this question."
            "Use it sparingly and refrain from using it if you already know the answer!"
        )

    def run_omega_tool(self, query: str = ""):
        """Use the tool."""
        try:

            with asection(f"WebSearchTool:"):
                with asection(f"Query:"):
                    aprint(query)

                # Run metasearch query:
                result = metasearch(query=query)

                with asection(f"Search result:"):
                    aprint(result)

                return result

        except Exception as e:
            traceback.print_exc()
            return f"Error: {type(e).__name__} with message: '{str(e)}' occurred while trying to search the web for: '{query}'."
