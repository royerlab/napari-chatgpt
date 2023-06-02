from langchain import OpenAI, WikipediaAPIWrapper
from langchain.agents import initialize_agent
from langchain.tools.wikipedia.tool import WikipediaQueryRun

from napari_chatgpt.omega.tools.search.web_search_tool import WebSearchTool

llm = OpenAI(temperature=0)

# tools = [GoogleSearchTool()]
# agent = initialize_agent(tools,
#                          llm,
#                          agent="zero-shot-react-description",
#                          verbose=True)
# result = agent.run("What is zebrahub? ")


wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

tools = [wiki, WebSearchTool()]
agent = initialize_agent(tools,
                         llm,
                         agent="conversational-react-description",
                         verbose=True)
result = agent.run("Who is Albert Einstein? ")
