from queue import Queue

from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import AsyncCallbackManager, CallbackManager
from langchain.memory import ConversationSummaryBufferMemory, \
    ConversationBufferWindowMemory

from napari_chatgpt.omega.omega_agent.agent import OmegaAgent
from napari_chatgpt.omega.omega_agent.agent_executor import \
    OmegaAgentExecutor
from napari_chatgpt.omega.omega_agent.prompts import PREFIX, SUFFIX, PERSONALITY
from napari_chatgpt.omega.tools.functions_info_tool import PythonFunctionsInfoTool
from napari_chatgpt.omega.tools.human_input_tool import HumanInputTool
from napari_chatgpt.omega.tools.napari_file_open_tool import NapariFileOpenTool
from napari_chatgpt.omega.tools.machinery.napari_plugin_tool import NapariPluginTool
from napari_chatgpt.omega.tools.napari_viewer_control_tool import \
    NapariViewerControlTool
from napari_chatgpt.omega.tools.napari_viewer_query_tool import NapariViewerQueryTool
from napari_chatgpt.omega.tools.napari_widget_maker_tool import NapariWidgetMakerTool
from napari_chatgpt.omega.tools.segmentation.cell_nuclei_segmentation import \
    CellNucleiSegmentationTool
from napari_chatgpt.omega.tools.web_image_search_tool import WebImageSearchTool
from napari_chatgpt.omega.tools.web_search_tool import WebSearchTool
from napari_chatgpt.omega.tools.wikipedia_query_tool import WikipediaQueryTool
from napari_chatgpt.utils.omega_plugins.discover_omega_plugins import \
    discover_omega_tools


def initialize_omega_agent(to_napari_queue: Queue = None,
                           from_napari_queue: Queue = None,
                           main_llm: BaseLanguageModel = None,
                           tool_llm: BaseLanguageModel = None,
                           memory_llm: BaseLanguageModel = None,
                           is_async: bool = False,
                           chat_callback_handler: BaseCallbackHandler = None,
                           tool_callback_handler: BaseCallbackHandler = None,
                           has_human_input_tool: bool = True,
                           memory_type: str = 'standard',
                           agent_personality: str = 'neutral',
                           ) -> OmegaAgentExecutor:
    chat_callback_manager = (AsyncCallbackManager(
        [chat_callback_handler]) if is_async else CallbackManager(
        [chat_callback_handler])) if chat_callback_handler else None

    tool_callback_manager = (CallbackManager(
        [tool_callback_handler])) if chat_callback_handler else None

    if memory_type == 'standard':
        memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True)
    elif memory_type == 'summarising':
        memory = ConversationSummaryBufferMemory(
            llm=memory_llm,
            memory_key="chat_history",
            return_messages=True)

    tools = [WikipediaQueryTool(callback_manager=tool_callback_manager),
             WebSearchTool(callback_manager=tool_callback_manager),
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
        tools.append(WebImageSearchTool(llm=tool_llm,
                                        to_napari_queue=to_napari_queue,
                                        from_napari_queue=from_napari_queue,
                                        callback_manager=tool_callback_manager))
        tools.append(CellNucleiSegmentationTool(llm=tool_llm,
                                                to_napari_queue=to_napari_queue,
                                                from_napari_queue=from_napari_queue,
                                                callback_manager=tool_callback_manager))
        tools.append(NapariViewerQueryTool(llm=tool_llm,
                                           to_napari_queue=to_napari_queue,
                                           from_napari_queue=from_napari_queue,
                                           callback_manager=tool_callback_manager))

        tool_classes = discover_omega_tools()

        for tool_class in tool_classes:
            if 'ExampleOmegaTool' in tool_class.__name__:
                # This is just an example/tempate!
                # Avoids having to test this with a separate repo!
                continue

            tools.append(NapariPluginTool(
                plugin_tool_instance=tool_class(),
                name=tool_class.name,
                type=tool_class.type,
                description=tool_class.description,
                prompt=tool_class.description,
                return_direct=tool_class.return_direct,
                lm=tool_llm,
                to_napari_queue=to_napari_queue,
                from_napari_queue=from_napari_queue,
                callback_manager=tool_callback_manager))

    # prepend the personality:
    PREFIX_ = PREFIX + PERSONALITY[agent_personality]

    agent = OmegaAgent.from_llm_and_tools(
        llm=main_llm,
        tools=tools,
        system_message=PREFIX_,
        human_message=SUFFIX,
        callback_manager=chat_callback_manager,
    )

    executor = OmegaAgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        callback_manager=chat_callback_manager
    )

    return executor
