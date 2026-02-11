"""Tool for requesting input from a human operator.

Allows the Omega agent to pause execution and ask the user a question
when it is uncertain about how to proceed. The prompt and input
functions are configurable (defaulting to ``print`` and ``input``).
"""

from collections.abc import Callable

from arbol import aprint, asection
from pydantic import Field

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool


def _print_func(text: str) -> None:
    """Default prompt function that prints the question to stdout."""
    print("\n")
    print(text)


class HumanInputTool(BaseOmegaTool):
    """Tool that asks the user for input when the agent needs guidance.

    Displays a question to the user and waits for a text response. The
    prompt display and input collection functions are pluggable via
    ``prompt_func`` and ``input_func`` attributes.

    Attributes:
        name: Tool identifier string.
        description: Human-readable description used by the LLM agent.
        prompt_func: Callable used to display the question to the user.
        input_func: Callable used to collect the user's response.
    """

    def __init__(self, **kwargs):
        """Initialize the HumanInputTool.

        Args:
            **kwargs: Keyword arguments forwarded to ``BaseOmegaTool``.
        """
        super().__init__(**kwargs)

        self.name = "HumanInputTool"
        self.description = (
            "You can ask a human for guidance when you think you "
            "got stuck or you are not sure what to do next. "
            "The input should be a question for the human."
        )
        self.prompt_func: Callable[[str], None] = Field(
            default_factory=lambda: _print_func
        )
        self.input_func: Callable = Field(default_factory=lambda: input)

    def run_omega_tool(self, query: str = ""):
        """Display a question to the user and return their response.

        Args:
            query: The question or prompt to present to the user.

        Returns:
            The user's text response as a string.
        """
        with asection(f"HumanInputTool:"):
            with asection(f"Query:"):
                aprint(query)

            self.prompt_func(query)
            return self.input_func()
