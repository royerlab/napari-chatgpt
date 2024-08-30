"""Module implements an agent that uses OpenAI's APIs function enabled API."""
from typing import Any, List, Tuple, Union

from langchain.agents import OpenAIFunctionsAgent
from langchain.agents.format_scratchpad.openai_functions import (
    format_to_openai_function_messages,
)
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.callbacks import Callbacks
from langchain_core.messages import (
    SystemMessage,
)

from napari_chatgpt.omega.napari_bridge import _get_viewer_info
from napari_chatgpt.omega.omega_agent.OmegaOpenAIFunctionsAgentOutputParser import \
    OpenAIFunctionsAgentOutputParser
from napari_chatgpt.omega.omega_agent.prompts import DIDACTICS


class OpenAIFunctionsOmegaAgent(OpenAIFunctionsAgent):

    # Convenience class to override some features of the OpenAIFunctionsAgent

    be_didactic: bool = False

    async def aplan(
        self,
        intermediate_steps: List[Tuple[AgentAction, str]],
        callbacks: Callbacks = None,
        **kwargs: Any,
    ) -> Union[AgentAction, AgentFinish]:
        """Async given input, decided what to do.

        Args:
            intermediate_steps: Steps the LLM has taken to date,
                along with observations.
            callbacks: Callbacks to use. Defaults to None.
            **kwargs: User inputs.

        Returns:
            Action specifying what tool to use.
            If the agent is finished, returns an AgentFinish.
            If the agent is not finished, returns an AgentAction.
        """
        agent_scratchpad = format_to_openai_function_messages(intermediate_steps)
        selected_inputs = {
            k: kwargs[k] for k in self.prompt.input_variables if k != "agent_scratchpad"
        }
        full_inputs = dict(**selected_inputs, agent_scratchpad=agent_scratchpad)
        prompt = self.prompt.format_prompt(**full_inputs)
        messages = prompt.to_messages()

        # Add viewer info to the messages:
        viewer_info = _get_viewer_info()
        if viewer_info:
            messages.insert(-1, SystemMessage(
                content="For reference, below is information about the napari viewer instance that is available to some of the tools: \n" + viewer_info,
                additional_kwargs=dict(
                    system_message_type="viewer_info"
                )
            ))

        # Add didactics to the messages:
        if self.be_didactic:
            messages.insert(-1, SystemMessage(
                content=DIDACTICS,
                additional_kwargs=dict(
                    system_message_type="didactics"
                )
            ))

        # predict the message:
        predicted_message = await self.llm.apredict_messages(
            messages, functions=self.functions, callbacks=callbacks
        )

        # parse the AI message:
        agent_decision = OpenAIFunctionsAgentOutputParser._parse_ai_message(predicted_message)
        return agent_decision