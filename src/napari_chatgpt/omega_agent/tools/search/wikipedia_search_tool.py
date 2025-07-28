import traceback

from arbol import asection, aprint

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool
from napari_chatgpt.utils.web.wikipedia import search_wikipedia


class WikipediaSearchTool(BaseOmegaTool):
    """
    A tool for searching Wikipedia articles.
    This tool can be used to find information on a wide range of topics.
    """

    def __init__(self, **kwargs):
        """
        Initialize the WikipediaSearchTool with a name and description for performing general Wikipedia searches.
        
        Additional keyword arguments are passed to the base class initializer.
        """
        super().__init__(**kwargs)

        # Tool name and description:

        self.name = "WikipediaSearchTool"
        self.description = (
            "Use this tool to answer general questions on topics covered by an encyclopedia "
            "such as historical events, scientific concepts, geography... "
            "for which you don't already have the answer. "
            "Input must be a plain text wikipedia search query. "
            "Do NOT use this tool if you already have the answer."
        )

    def run_omega_tool(self, query: str = ""):
        """
        Searches Wikipedia for the given query and returns the result.
        
        Parameters:
            query (str): The search term to look up on Wikipedia.
        
        Returns:
            str: The search result from Wikipedia, or an error message if the search fails.
        """
        try:

            with asection(f"WikipediaSearchTool:"):
                with asection(f"Query:"):
                    aprint(query)

                # Run wikipedia search:
                result = search_wikipedia(query=query)

                with asection(f"Result:"):
                    aprint(result)

                return result

        except Exception as e:
            traceback.print_exc()
            return f"Error: {type(e).__name__} with message: '{str(e)}' occured while trying to search wikipedia for: '{query}'."
