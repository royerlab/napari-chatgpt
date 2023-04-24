from queue import Queue

from langchain.callbacks import CallbackManager, \
    AsyncCallbackManager, BaseCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseLanguageModel

from napari_chatgpt.omega.omega_agent.omega_agent import OmegaAgent
from napari_chatgpt.omega.omega_agent.omega_agent_executor import \
    OmegaAgentExecutor
from napari_chatgpt.omega.omega_agent.omega_prompts import PREFIX, SUFFIX
from napari_chatgpt.tools.functions_info import PythonFunctionsInfoTool
from napari_chatgpt.tools.google_search_tool import GoogleSearchTool
from napari_chatgpt.tools.human_input_tool import HumanInputTool
from napari_chatgpt.tools.math_tool import MathTool
from napari_chatgpt.tools.napari_file_open import NapariFileOpenTool
from napari_chatgpt.tools.napari_viewer_control import NapariViewerControlTool
from napari_chatgpt.tools.napari_widget_maker import NapariWidgetMakerTool
from napari_chatgpt.tools.web_search_tool import WebSearchTool
from napari_chatgpt.tools.wikipedia_query_tool import WikipediaQueryTool


def initialize_omega_agent(to_napari_queue: Queue = None,
                           from_napari_queue: Queue = None,
                           main_llm: BaseLanguageModel = None,
                           tool_llm: BaseLanguageModel = None,
                           is_async: bool = False,
                           chat_callback_handler: BaseCallbackHandler = None,
                           tool_callback_handler: BaseCallbackHandler = None,
                           has_human_input_tool: bool = True
                           ) -> OmegaAgentExecutor:
    chat_callback_manager = (AsyncCallbackManager(
        [chat_callback_handler]) if is_async else CallbackManager(
        [chat_callback_handler])) if chat_callback_handler else None

    tool_callback_manager = (CallbackManager(
        [tool_callback_handler])) if chat_callback_handler else None

    memory = ConversationBufferMemory(memory_key="chat_history",
                                      return_messages=True)

    tools = [WikipediaQueryTool(callback_manager=tool_callback_manager),
             WebSearchTool(callback_manager=tool_callback_manager),
             MathTool(llm=tool_llm, callback_manager=tool_callback_manager),
             PythonFunctionsInfoTool(callback_manager=tool_callback_manager),
             # FileDownloadTool(),
             # PythonREPLTool()
             ]

    if has_human_input_tool:
        tools.append(HumanInputTool(callback_manager=tool_callback_manager))

    if to_napari_queue:
        tools.append(NapariViewerControlTool(llm=tool_llm,
                                             to_napari_queue=to_napari_queue,
                                             from_napari_queue=from_napari_queue,
                                             callback_manager=tool_callback_manager))
        tools.append(NapariWidgetMakerTool(llm=tool_llm,
                                           to_napari_queue=to_napari_queue,
                                           from_napari_queue=from_napari_queue,
                                           callback_manager=tool_callback_manager))
        tools.append(NapariFileOpenTool(llm=tool_llm,
                                        to_napari_queue=to_napari_queue,
                                        from_napari_queue=from_napari_queue,
                                        callback_manager=tool_callback_manager))

    agent = OmegaAgent.from_llm_and_tools(
        llm=main_llm,
        tools=tools,
        system_message=PREFIX,
        human_message=SUFFIX,
        callback_manager=chat_callback_manager
    )

    executor = OmegaAgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        callback_manager=chat_callback_manager
    )

    return executor
