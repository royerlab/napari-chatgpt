"""Tool for searching Wikipedia articles.

Provides the Omega agent with the ability to look up encyclopedic
information on historical events, scientific concepts, geography, and
other topics covered by Wikipedia.
"""

import traceback

from arbol import aprint, asection

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool
from napari_chatgpt.utils.web.wikipedia import search_wikipedia


class WikipediaSearchTool(BaseOmegaTool):
    """Tool for searching Wikipedia for encyclopedic information.

    Accepts a plain-text search query and returns a summary extracted
    from the most relevant Wikipedia article. Best suited for general
    knowledge questions the LLM cannot answer from its training data.

    Attributes:
        name: Tool identifier string.
        description: Human-readable description used by the LLM agent.
    """

    def __init__(self, **kwargs):
        """Initialize the WikipediaSearchTool.

        Args:
            **kwargs: Keyword arguments forwarded to ``BaseOmegaTool``.
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
        """Search Wikipedia and return a summary of the best-matching article.

        Args:
            query: Plain-text Wikipedia search query.

        Returns:
            A summary string from the matching Wikipedia article, or an
            error message if the search fails.
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
            return f"Error: {type(e).__name__} with message: '{str(e)}' occurred while trying to search wikipedia for: '{query}'."
