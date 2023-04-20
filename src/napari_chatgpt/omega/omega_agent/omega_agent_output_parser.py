from langchain.agents.conversational_chat.output_parser import ConvoOutputParser

from napari_chatgpt.omega.omega_agent.omega_prompts import FORMAT_INSTRUCTIONS


class OmegaAgentOutputParser(ConvoOutputParser):
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS
