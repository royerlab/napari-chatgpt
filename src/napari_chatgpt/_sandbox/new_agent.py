from napari_chatgpt.utils.api_keys.api_key import set_api_key

set_api_key('OpenAI')

from langchain.agents import initialize_agent, AgentType
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


llm = ChatOpenAI(temperature=0, model="gpt-4-1106-preview")

# Define a list of tools offered by the agent
tools = [WikipediaQueryTool(callback_manager=None),
         WebSearchTool(callback_manager=None),
         PythonFunctionsInfoTool(callback_manager=None),
         ExceptionCatcherTool(callback_manager=None),
         PythonCodeExecutionTool(callback_manager=None)
         ]

executor = initialize_agent(
    tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True,
)

# Do this so we can see exactly what's going on under the hood
# from langchain.globals import set_debug
#
# set_debug(True)

executor.run("Can you execute this piece of python code: 'list(x**2 for x in [0,1,2,3,4])' and return to me the result?")

executor.run("What information can you find about what happened on dec 2023?")

