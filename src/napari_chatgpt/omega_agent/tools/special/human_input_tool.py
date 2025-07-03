"""Tool for asking human input."""

from typing import Callable

from arbol import asection, aprint
from pydantic import Field

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool


def _print_func(text: str) -> None:
    print("\n")
    print(text)


class HumanInputTool(BaseOmegaTool):
    """
    Tool that asks the user for input.
    This tool is useful when the agent is unsure about the next step.
    """

    def __init__(self, **kwargs):
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
        with asection(f"HumanInputTool:"):
            with asection(f"Query:"):
                aprint(query)

            """Use the Human input tool."""
            self.prompt_func(query)
            return self.input_func()
