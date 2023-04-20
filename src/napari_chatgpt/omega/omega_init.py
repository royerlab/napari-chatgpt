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
from napari_chatgpt.omega.omega_agent.omega_prompts import PREFIX, SUFFIX
from napari_chatgpt.tools.functions_info import PythonFunctionsInfoTool
from napari_chatgpt.tools.google_search_tool import GoogleSearchTool
from napari_chatgpt.tools.napari_viewer_control import NapariViewerControlTool
from napari_chatgpt.tools.napari_widget_maker import NapariWidgetMakerTool


def initialize_omega_agent(to_napari_queue: Queue = None,
                           from_napari_queue: Queue = None,
                           main_llm: BaseLanguageModel = None,
                           ) -> OmegaAgentExecutor:

    main_llm = main_llm or ChatOpenAI(model_name='gpt-3.5-turbo',
                                      temperature=0
                                      )

    memory = ConversationBufferMemory(memory_key="chat_history",
                                      return_messages=True)

    wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    tools = [wiki,
             GoogleSearchTool(),
             _get_llm_math(main_llm),
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

    agent = OmegaAgent.from_llm_and_tools(
        llm=main_llm,
        tools=tools,
        system_message=PREFIX,
        human_message=SUFFIX,
    )

    executor = OmegaAgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True
    )

    return executor


