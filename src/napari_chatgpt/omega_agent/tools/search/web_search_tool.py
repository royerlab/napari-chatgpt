"""Tool for performing web searches to answer questions.

Provides the Omega agent with the ability to search the web using a
metasearch backend when it lacks the knowledge to answer a question
directly.
"""

import traceback

from arbol import aprint, asection

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool
from napari_chatgpt.utils.web.metasearch import metasearch


class WebSearchTool(BaseOmegaTool):
    """Tool for searching the web using a metasearch backend.

    Accepts a plain-text search query and returns aggregated results from
    multiple search engines. Intended for cases where the LLM does not
    already know the answer.

    Attributes:
        name: Tool identifier string.
        description: Human-readable description used by the LLM agent.
    """

    def __init__(self, **kwargs):
        """Initialize the WebSearchTool.

        Args:
            **kwargs: Keyword arguments forwarded to ``BaseOmegaTool``.
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
        """Execute a web search and return the results.

        Args:
            query: Plain-text search query string.

        Returns:
            Search results as a formatted string, or an error message
            if the search fails.
        """
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
