from queue import Queue

import langchain
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import AsyncCallbackManager, CallbackManager
from langchain.schema import BaseMemory

from napari_chatgpt.omega.omega_agent.agent import OmegaAgent
from napari_chatgpt.omega.omega_agent.agent_executor import \
    OmegaAgentExecutor
from napari_chatgpt.omega.omega_agent.prompts import PREFIX, SUFFIX, PERSONALITY
from napari_chatgpt.omega.tools.napari.cell_nuclei_segmentation import \
    CellNucleiSegmentationTool
from napari_chatgpt.omega.tools.napari.file_open_tool import NapariFileOpenTool
from napari_chatgpt.omega.tools.napari.image_denoising import ImageDenoisingTool
from napari_chatgpt.omega.tools.napari.viewer_control_tool import \
    NapariViewerControlTool
from napari_chatgpt.omega.tools.napari.viewer_query_tool import \
    NapariViewerQueryTool
from napari_chatgpt.omega.tools.napari.widget_maker_tool import \
    NapariWidgetMakerTool
from napari_chatgpt.omega.tools.napari_plugin_tool import \
    NapariPluginTool
from napari_chatgpt.omega.tools.search.web_image_search_tool import \
    WebImageSearchTool
from napari_chatgpt.omega.tools.search.web_search_tool import WebSearchTool
from napari_chatgpt.omega.tools.search.wikipedia_query_tool import \
    WikipediaQueryTool
from napari_chatgpt.omega.tools.special.exception_catcher_tool import \
    ExceptionCatcherTool
from napari_chatgpt.omega.tools.special.functions_info_tool import \
    PythonFunctionsInfoTool
from napari_chatgpt.omega.tools.special.human_input_tool import HumanInputTool
from napari_chatgpt.omega.tools.special.python_repl import PythonCodeExecutionTool
from napari_chatgpt.utils.omega_plugins.discover_omega_plugins import \
    discover_omega_tools

# Default verbosity to False:
langchain.verbose = False


def initialize_omega_agent(to_napari_queue: Queue = None,
                           from_napari_queue: Queue = None,
                           main_llm: BaseLanguageModel = None,
                           tool_llm: BaseLanguageModel = None,
                           is_async: bool = False,
                           chat_callback_handler: BaseCallbackHandler = None,
                           tool_callback_handler: BaseCallbackHandler = None,
                           has_human_input_tool: bool = True,
                           memory: BaseMemory = None,
                           agent_personality: str = 'neutral',
                           fix_imports: bool = True,
                           install_missing_packages: bool = True,
                           fix_bad_calls: bool = True,
                           autofix_mistakes: bool = False,
                           autofix_widget: bool = False,
                           verbose: bool = False
                           ) -> OmegaAgentExecutor:

    chat_callback_manager = (AsyncCallbackManager(
        [chat_callback_handler]) if is_async else CallbackManager(
        [chat_callback_handler])) if chat_callback_handler else None

    tool_callback_manager = (CallbackManager(
        [tool_callback_handler])) if chat_callback_handler else None

    tools = [WikipediaQueryTool(callback_manager=tool_callback_manager),
             WebSearchTool(callback_manager=tool_callback_manager),
             PythonFunctionsInfoTool(callback_manager=tool_callback_manager),
             ExceptionCatcherTool(callback_manager=tool_callback_manager),
             # FileDownloadTool(),
             PythonCodeExecutionTool(callback_manager=tool_callback_manager)
             ]

    if has_human_input_tool:
        tools.append(HumanInputTool(callback_manager=tool_callback_manager))

    if to_napari_queue:

        kwargs = {'llm': tool_llm,
                  'to_napari_queue': to_napari_queue,
                  'from_napari_queue': from_napari_queue,
                  'callback_manager': tool_callback_manager,
                  'fix_imports': fix_imports,
                  'install_missing_packages': install_missing_packages,
                  'fix_bad_calls': fix_bad_calls,
                  'verbose': verbose
                  }

        tools.append(NapariViewerControlTool(**kwargs, return_direct=not autofix_mistakes))
        tools.append(NapariViewerQueryTool(**kwargs, return_direct=not autofix_mistakes))
        tools.append(NapariWidgetMakerTool(**kwargs, return_direct=not autofix_widget))
        tools.append(NapariFileOpenTool(**kwargs))
        tools.append(WebImageSearchTool(**kwargs))
        tools.append(CellNucleiSegmentationTool(**kwargs))
        tools.append(ImageDenoisingTool(**kwargs))


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
        verbose=verbose,
        callback_manager=chat_callback_manager,
    )

    executor = OmegaAgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=verbose,
        callback_manager=chat_callback_manager
    )

    return executor
