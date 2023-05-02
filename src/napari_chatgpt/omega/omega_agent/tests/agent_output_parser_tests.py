from napari_chatgpt.omega.omega_agent.agent_output_parser import \
    OmegaAgentOutputParser

__omega_agent_output_example_1 = \
    """
    Action: 
    WikipediaTool
    
    Input: 
    Albert Einstein
    
    """

__omega_agent_output_example_2 = \
    """Action: FinalAnswer
    
    Input: Hello! How can I assist you today?'"""


def test_omega_agent_output_parser():
    parser = OmegaAgentOutputParser()

    result = parser.parse(__omega_agent_output_example_1)
    print(result)
    assert result.tool == 'WikipediaTool'
    assert result.tool_input == 'Albert Einstein'

    result = parser.parse(__omega_agent_output_example_1)

    print(result)

    assert result.tool == 'FinalAnswer'
    assert result.tool_input == 'Hello! How can I assist you today?'
