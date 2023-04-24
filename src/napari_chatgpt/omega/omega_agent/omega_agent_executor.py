from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferWindowMemory


class OmegaAgentExecutor(AgentExecutor):
    """Consists of an agent using tools."""

    max_iterations = 7

    memory = ConversationBufferWindowMemory()
