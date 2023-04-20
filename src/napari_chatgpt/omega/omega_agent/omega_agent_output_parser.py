from langchain.agents.conversational_chat.output_parser import ConvoOutputParser

from napari_chatgpt.agents.omega.omega_prompts import FORMAT_INSTRUCTIONS


class OmegaAgentOutputParser(ConvoOutputParser):
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS
