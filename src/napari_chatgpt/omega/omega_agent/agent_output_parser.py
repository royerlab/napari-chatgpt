import re
import traceback
from typing import Union, List

from langchain.agents import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish

from napari_chatgpt.omega.omega_agent.prompts import \
    OMEGA_FORMAT_INSTRUCTIONS


class OmegaAgentOutputParser(AgentOutputParser):

    tool_names: List[str]

    def get_format_instructions(self) -> str:
        return OMEGA_FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:

        try:
            # Clean up output:
            cleaned_output = text.strip()

            # Add FinalAnswer as a special tool/action:
            tool_names = self.tool_names+['FinalAnswer']

            # Parse:
            result = parse_command(tool_names, cleaned_output)

            if not result:
                result = AgentFinish({"output": cleaned_output}, cleaned_output)
            else:
                action_str, input_str = result

                if action_str.lower() == "finalanswer":
                    result = AgentFinish({"output": input_str}, cleaned_output)
                else:
                    result = AgentAction(action_str, input_str, cleaned_output)

            return result

        except Exception as e:
            traceback.print_exc()
            return AgentFinish({"output": cleaned_output}, cleaned_output)


def parse_command(tool_names: List[str], command_string: str):

    # Convert to lower case for more robust substring finding:
    command_string_lower_case = command_string.lower()

    for tool_name in tool_names:
        tool_name_sc = tool_name.lower()+':'
        if tool_name_sc in command_string_lower_case:

            # action/tool name is:
            action_str = tool_name

            # Position:
            index = command_string_lower_case.find(tool_name_sc)

            # get the input:
            input_str = command_string[index + len(tool_name_sc):]

            # Cleanup:
            action_str = action_str.strip()
            input_str = input_str.strip()

            return action_str, input_str

    return None


    # pattern = r'^([a-zA-Z]+):(.*)'
    # match = re.match(pattern, command_string, re.DOTALL | re.MULTILINE)
    # if match:
    #     action_str = match.group(1).strip()
    #     input_str = match.group(2).strip()
    #     return action_str, input_str
    # else:
    #     return None
