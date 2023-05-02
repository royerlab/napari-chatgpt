"""An agent designed to hold a conversation in addition to using tools."""
from __future__ import annotations

from typing import List, Tuple, Any

from langchain.agents import ConversationalChatAgent, AgentOutputParser
from langchain.schema import AgentAction, BaseMessage, AIMessage, HumanMessage

from napari_chatgpt.omega.omega_agent.agent_output_parser import \
    OmegaAgentOutputParser
from napari_chatgpt.omega.omega_agent.prompts import \
    TEMPLATE_TOOL_RESPONSE


class OmegaAgent(ConversationalChatAgent):
    """An agent designed to hold a conversation in addition to using tools."""

    output_parser = OmegaAgentOutputParser()

    @classmethod
    def _get_default_output_parser(cls, **kwargs: Any) -> AgentOutputParser:
        return OmegaAgentOutputParser()

    def _construct_scratchpad(
            self, intermediate_steps: List[Tuple[AgentAction, str]]
    ) -> List[BaseMessage]:
        """Construct the scratchpad that lets the agent continue its thought process."""
        thoughts: List[BaseMessage] = []
        for action, observation in intermediate_steps:
            thoughts.append(AIMessage(content=action.log))
            human_message = HumanMessage(
                content=TEMPLATE_TOOL_RESPONSE.format(observation=observation)
            )
            thoughts.append(human_message)
        return thoughts
