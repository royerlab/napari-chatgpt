"""Module implements an agent that uses OpenAI's APIs function enabled API."""
from typing import Any, List, Tuple, Union

from langchain.agents import OpenAIFunctionsAgent
from langchain.agents.format_scratchpad.openai_functions import (
    format_to_openai_function_messages,
)
from langchain.agents.output_parsers.openai_functions import (
    OpenAIFunctionsAgentOutputParser,
)
from langchain.callbacks.manager import Callbacks
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import (
    SystemMessage,
)

# global Variable to exchange information with the viewer:
_viewer_info = None

def set_viewer_info(viewer_info):
    global _viewer_info
    _viewer_info = viewer_info

class OpenAIFunctionsOmegaAgent(OpenAIFunctionsAgent):

    # Convenience class to override some features of the OpenAIFunctionsAgent

    async def aplan(
            self,
            intermediate_steps: List[Tuple[AgentAction, str]],
            callbacks: Callbacks = None,
            **kwargs: Any,
    ) -> Union[AgentAction, AgentFinish]:
        """Given input, decided what to do.

        Args:
            intermediate_steps: Steps the LLM has taken to date,
                along with observations
            **kwargs: User inputs.

        Returns:
            Action specifying what tool to use.
        """
        agent_scratchpad = format_to_openai_function_messages(
            intermediate_steps)
        selected_inputs = {
            k: kwargs[k] for k in self.prompt.input_variables if
            k != "agent_scratchpad"
        }
        full_inputs = dict(**selected_inputs, agent_scratchpad=agent_scratchpad)
        prompt = self.prompt.format_prompt(**full_inputs)
        messages = prompt.to_messages()

        # Add viewer info to the messages:
        global _viewer_info
        if _viewer_info:
            messages.insert(-1, SystemMessage(
                content="For reference, below is information about the napari viewer instance that is available to some of the tools: \n" + _viewer_info,
                additional_kwargs=dict(
                    system_message_type="viewer_info"
                )
            ))

        predicted_message = await self.llm.apredict_messages(
            messages, functions=self.functions, callbacks=callbacks
        )
        agent_decision = OpenAIFunctionsAgentOutputParser._parse_ai_message(
            predicted_message
        )
        return agent_decision