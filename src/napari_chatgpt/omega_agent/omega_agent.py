from typing import Optional

from litemind.agent.agent import Agent
from litemind.agent.tools.toolset import ToolSet
from litemind.apis.base_api import BaseApi


class OmegaAgent(Agent):

    def __init__(
        self,
        api: BaseApi,
        name: str = "Agent",
        model_name: Optional[str] = None,
        temperature: float = 0.0,
        toolset: Optional[ToolSet] = None,
        **kwargs,
    ):
        """
        Initialize an OmegaAgent instance with the specified API, model configuration, and optional toolset.
        
        Parameters:
            name (str, optional): The agent's display name.
            model_name (str, optional): Identifier for the language model to use.
            temperature (float, optional): Controls randomness in text generation.
            toolset (ToolSet, optional): Collection of tools available to the agent.
            **kwargs: Additional keyword arguments forwarded to the base Agent.
        """

        super().__init__(
            api=api,
            name=name,
            model_name=model_name,
            temperature=temperature,
            toolset=toolset,
            **kwargs,
        )
