"""Omega agent definition.

Provides ``OmegaAgent``, a thin specialisation of LiteMind's ``Agent``
tailored for the napari-chatgpt plugin. Future Omega-specific behaviour
(e.g. custom memory, conversation hooks) should be added here.
"""

from litemind.agent.agent import Agent
from litemind.agent.tools.toolset import ToolSet
from litemind.apis.base_api import BaseApi


class OmegaAgent(Agent):
    """LLM-powered agent for interactive image processing within napari.

    Extends ``litemind.agent.agent.Agent`` to serve as the central
    orchestrator of the Omega system. It is configured with a
    ``ToolSet`` containing napari-aware tools and is driven by a
    system prompt that establishes its image-analysis expertise.
    """

    def __init__(
        self,
        api: BaseApi,
        name: str = "Agent",
        model_name: str | None = None,
        temperature: float = 0.0,
        toolset: ToolSet | None = None,
        **kwargs,
    ):
        """Create a new OmegaAgent.

        Args:
            api: The LiteMind API backend to use for LLM calls.
            name: Human-readable name for this agent.
            model_name: Identifier of the LLM model to use. ``None``
                means the API default.
            temperature: Sampling temperature for text generation.
            toolset: Collection of tools the agent may invoke.
            **kwargs: Additional keyword arguments forwarded to the
                parent ``Agent`` constructor.
        """

        super().__init__(
            api=api,
            name=name,
            model_name=model_name,
            temperature=temperature,
            toolset=toolset,
            **kwargs,
        )
