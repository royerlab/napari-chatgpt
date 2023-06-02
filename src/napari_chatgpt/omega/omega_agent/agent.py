"""An agent designed to hold a conversation in addition to using tools."""
from __future__ import annotations

from typing import Any, List, Optional, Sequence, Tuple

from langchain.agents import ConversationalChatAgent
from langchain.agents.agent import Agent, AgentOutputParser
from langchain.agents.conversational_chat.prompt import (
    PREFIX,
    SUFFIX,
    TEMPLATE_TOOL_RESPONSE,
)
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains import LLMChain
from langchain.schema import (
    AgentAction,
    AIMessage,
    BaseMessage,
    HumanMessage,
)
from langchain.tools.base import BaseTool

from napari_chatgpt.omega.omega_agent.agent_output_parser import \
    OmegaAgentOutputParser
from napari_chatgpt.omega.omega_agent.prompts import \
    TEMPLATE_TOOL_RESPONSE


class OmegaAgent(ConversationalChatAgent):
    """An agent designed to hold a conversation in addition to using tools."""

    # output_parser = OmegaAgentOutputParser()
    #
    # @classmethod
    # def _get_default_output_parser(cls, **kwargs: Any) -> AgentOutputParser:
    #     return cls.output_parser

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

    @classmethod
    def from_llm_and_tools(
            cls,
            llm: BaseLanguageModel,
            tools: Sequence[BaseTool],
            callback_manager: Optional[BaseCallbackManager] = None,
            output_parser: Optional[AgentOutputParser] = None,
            system_message: str = PREFIX,
            human_message: str = SUFFIX,
            input_variables: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> Agent:
        """Construct an agent from an LLM and tools."""
        cls._validate_tools(tools)
        tool_names = list([tool.name for tool in tools])
        _output_parser = OmegaAgentOutputParser(tool_names=tool_names)
        prompt = cls.create_prompt(
            tools,
            system_message=system_message,
            human_message=human_message,
            input_variables=input_variables,
            output_parser=_output_parser,
        )
        llm_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            callback_manager=callback_manager,
        )

        return cls(
            llm_chain=llm_chain,
            allowed_tools=tool_names,
            output_parser=_output_parser,
            **kwargs,
        )
