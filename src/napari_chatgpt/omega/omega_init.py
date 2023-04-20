from queue import Queue
from typing import Optional

from langchain import WikipediaAPIWrapper
from langchain.agents.load_tools import _get_llm_math, _get_human_tool
from langchain.callbacks import BaseCallbackManager, CallbackManager
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseLanguageModel
from langchain.tools.wikipedia.tool import WikipediaQueryRun

from napari_chatgpt.omega.omega_agent.omega_agent import OmegaAgent
from napari_chatgpt.omega.omega_agent.omega_agent_executor import \
    OmegaAgentExecutor
from napari_chatgpt.omega.omega_agent.omega_callback_handler import \
    OmegaCallbackHandler
from napari_chatgpt.tools.functions_info import PythonFunctionsInfoTool
from napari_chatgpt.tools.google_search_tool import GoogleSearchTool
from napari_chatgpt.tools.napari_viewer_control import NapariViewerControlTool
from napari_chatgpt.tools.napari_widget_maker import NapariWidgetMakerTool


def initialize_omega_agent(to_napari_queue: Queue = None,
                           from_napari_queue: Queue = None,
                           llm: BaseLanguageModel = None,
                           agent_callback_manager: Optional[BaseCallbackManager] = None,
                           ) -> OmegaAgentExecutor:



    wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    llm_for_math = ChatOpenAI(temperature=0)
    tools = [wiki,
             GoogleSearchTool(),
             _get_llm_math(llm_for_math),
             PythonFunctionsInfoTool(),
             _get_human_tool(),
             # FileDownloadTool(),
             # PythonREPLTool()
             ]

    if to_napari_queue:
        tools.append(NapariViewerControlTool(to_napari_queue=to_napari_queue,
                                             from_napari_queue=from_napari_queue))
        tools.append(NapariWidgetMakerTool(to_napari_queue=to_napari_queue,
                                           from_napari_queue=from_napari_queue))

    llm = llm or ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)

    memory = ConversationBufferMemory(memory_key="chat_history",
                                      return_messages=True)

    if not agent_callback_manager:
        agent_callback_manager = CallbackManager([])

    agent_callback_manager.add_handler(OmegaCallbackHandler())

    agent = OmegaAgent.from_llm_and_tools(
        llm=llm,
        tools=tools,
        callback_manager=agent_callback_manager
    )

    executor = OmegaAgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        callback_manager=agent_callback_manager,
        memory=memory,
    )

    return executor


