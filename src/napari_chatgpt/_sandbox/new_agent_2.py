from langchain.agents.format_scratchpad.openai_tools import \
    format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import \
    OpenAIToolsAgentOutputParser
from langchain_community.tools.convert_to_openai import \
    format_tool_to_openai_tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from napari_chatgpt.utils.api_keys.api_key import set_api_key

set_api_key('OpenAI')

from langchain.agents import initialize_agent, AgentType, AgentExecutor
from langchain_community.chat_models import ChatOpenAI

from napari_chatgpt.omega.tools.search.web_search_tool import WebSearchTool
from napari_chatgpt.omega.tools.search.wikipedia_query_tool import \
    WikipediaQueryTool
from napari_chatgpt.omega.tools.special.exception_catcher_tool import \
    ExceptionCatcherTool
from napari_chatgpt.omega.tools.special.functions_info_tool import \
    PythonFunctionsInfoTool
from napari_chatgpt.omega.tools.special.python_repl import \
    PythonCodeExecutionTool

from langchain.tools import BearlyInterpreterTool, DuckDuckGoSearchRun

llm = ChatOpenAI(temperature=0, model="gpt-4-1106-preview")

# Define a list of tools offered by the agent
lc_tools = [WikipediaQueryTool(callback_manager=None),
         WebSearchTool(callback_manager=None),
         PythonFunctionsInfoTool(callback_manager=None),
         ExceptionCatcherTool(callback_manager=None),
         PythonCodeExecutionTool(callback_manager=None)
         ]

# Convert tools to OpenAI tool format:
oai_tools = [format_tool_to_openai_tool(tool) for tool in lc_tools]

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
    }
    | prompt
    | llm.bind(tools=oai_tools)
    | OpenAIToolsAgentOutputParser()
)

agent_executor = AgentExecutor(agent=agent, tools=lc_tools, verbose=True)

# # Do this so we can see exactly what's going on under the hood
# from langchain.globals import set_debug
#
# set_debug(True)

agent_executor.invoke({'input':"Can you execute this piece of python code: 'list(x**2 for x in [0,1,2,3,4])' and return to me the result?"})

agent_executor.invoke({'input':"What information can you find about what happened on dec 18th 2023?"})

