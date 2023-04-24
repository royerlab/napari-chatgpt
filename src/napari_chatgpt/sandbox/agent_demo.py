from langchain import OpenAI
from langchain.agents import load_tools, initialize_agent

llm = OpenAI(temperature=0)
tool_names = ["wikipedia"]
tools = load_tools(tool_names)
agent = initialize_agent(tools, llm, agent="zero-shot-react-description",
                         verbose=True)
result = agent.run(
    "Tell me more about powergraphs, a formalism for representing graphs and networks ")

print(result)
