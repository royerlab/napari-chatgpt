from litemind.agent.agent import Agent
from litemind.agent.tools.toolset import ToolSet
from litemind.apis.base_api import BaseApi


class OmegaAgent(Agent):

    def __init__(
        self,
        api: BaseApi,
        name: str = "Agent",
        model_name: str | None = None,
        temperature: float = 0.0,
        toolset: ToolSet | None = None,
        **kwargs,
    ):
        """
        Create a new agent.

        Parameters
        ----------
        api: BaseApi
            The API to use.
        name: str
            The name of the agent.
        model_name: str
            The name of the model to use.
        temperature: float
            The temperature to use for text generation.
        toolset: ToolSet
            The toolset to use.
        kwargs: Any
            Additional keyword arguments to pass to the API.
        """

        super().__init__(
            api=api,
            name=name,
            model_name=model_name,
            temperature=temperature,
            toolset=toolset,
            **kwargs,
        )
