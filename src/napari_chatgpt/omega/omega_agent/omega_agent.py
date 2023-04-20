"""An agent designed to hold a conversation in addition to using tools."""
from __future__ import annotations

from langchain.agents import ConversationalChatAgent

from napari_chatgpt.omega.omega_agent.omega_agent_output_parser import \
    OmegaAgentOutputParser


class OmegaAgent(ConversationalChatAgent):
    """An agent designed to hold a conversation in addition to using tools."""

    output_parser = OmegaAgentOutputParser()
