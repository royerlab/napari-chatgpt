from langchain import WikipediaAPIWrapper
from langchain.agents import AgentType
from langchain.agents import initialize_agent
from langchain.agents.load_tools import _get_llm_math
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.tools.python.tool import PythonREPLTool
from langchain.tools.wikipedia.tool import WikipediaQueryRun

from napari_chatgpt.omega.tools.search.web_search_tool import WebSearchTool

llm = ChatOpenAI(temperature=0)

memory = ConversationBufferMemory(memory_key="chat_history",
                                  return_messages=True)

wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
tools = [wiki, WebSearchTool(), _get_llm_math(llm), PythonREPLTool()]

system_message = """Omega is a large language model trained by OpenAI.

Omega is designed to be able to assist with a wide range of tasks, 
from answering simple questions to providing in-depth explanations and 
discussions on a wide range of topics. As a language model, Omega is 
able to generate human-like text based on the input it receives, allowing 
it to engage in natural-sounding conversations and provide responses that 
are coherent and relevant to the topic at hand.

Omega is constantly learning and improving, and its capabilities are 
constantly evolving. It is able to process and understand large amounts of text, 
and can use this knowledge to provide accurate and informative responses to a wide 
range of questions. Additionally, Omega is able to generate its own text based 
on the input it receives, allowing it to engage in discussions and provide explanations 
and descriptions on a wide range of topics.

Overall, Omega is a powerful system that can help with a wide range of tasks 
and provide valuable insights and information on a wide range of topics. 
Whether you need help with a specific question or just want to have a conversation 
about a particular topic, Assistant is here to assist."""

human_message = """TOOLS
------
Omega can ask the user to use tools to look up information that may be helpful 
in answering the users original question. The tools the human can use are:

{{tools}}

{format_instructions}

USER'S INPUT
--------------------
Here is the user's input (remember to respond with a markdown code snippet of a 
json blob with a single action, and NOTHING else):

{{{{input}}}}"""

agent_kwargs = {'system_message': system_message,
                'human_message': human_message}

agent_chain = initialize_agent(tools,
                               llm,
                               agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                               verbose=True,
                               memory=memory,
                               agent_kwargs=agent_kwargs
                               )

while True:
    query = input()
    if query == 'quit':
        break
    print(agent_chain.run(input=query))
