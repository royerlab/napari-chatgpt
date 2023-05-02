from langchain.agents import AgentExecutor


class OmegaAgentExecutor(AgentExecutor):
    """Consists of an agent using tools."""

    max_iterations = 5
    early_stopping_method = 'generate'
