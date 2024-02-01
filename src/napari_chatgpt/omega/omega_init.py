from queue import Queue

import langchain
from arbol import aprint
from langchain.agents import AgentExecutor
from langchain.agents.conversational_chat.prompt import SUFFIX
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import AsyncCallbackManager, CallbackManager
from langchain.schema import BaseMemory
from langchain_core.messages import SystemMessage
from langchain_core.prompts import MessagesPlaceholder


from napari_chatgpt.omega.omega_agent.prompts import SYSTEM, PERSONALITY
from napari_chatgpt.omega.tools.napari.cell_nuclei_segmentation_tool import \
    CellNucleiSegmentationTool
from napari_chatgpt.omega.tools.napari.file_open_tool import \
        NapariFileOpenTool
from napari_chatgpt.omega.tools.napari.image_denoising_tool import \
    ImageDenoisingTool
from napari_chatgpt.omega.tools.napari.viewer_control_tool import \
    NapariViewerControlTool
from napari_chatgpt.omega.tools.napari.viewer_execution_tool import \
    NapariViewerExecutionTool
from napari_chatgpt.omega.tools.napari.viewer_query_tool import \
    NapariViewerQueryTool
from napari_chatgpt.omega.tools.napari.viewer_vision_tool import \
    NapariViewerVisionTool
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
from napari_chatgpt.omega.tools.special.pip_install_tool import PipInstallTool
from napari_chatgpt.omega.tools.special.python_repl import \
    PythonCodeExecutionTool
from napari_chatgpt.utils.configuration.app_configuration import \
    AppConfiguration
from napari_chatgpt.utils.notebook.jupyter_notebook import JupyterNotebookFile
from napari_chatgpt.utils.omega_plugins.discover_omega_plugins import \
    discover_omega_tools
from napari_chatgpt.utils.openai.gpt_vision import is_gpt_vision_available
from napari_chatgpt.utils.system.is_apple_silicon import is_apple_silicon

# Default verbosity to False:
langchain.verbose = False

def initialize_omega_agent(to_napari_queue: Queue = None,
                           from_napari_queue: Queue = None,
                           main_llm_model_name: str = None,
                           main_llm: BaseLanguageModel = None,
                           tool_llm: BaseLanguageModel = None,
                           is_async: bool = False,
                           chat_callback_handler: BaseCallbackHandler = None,
                           tool_callback_handler: BaseCallbackHandler = None,
                           notebook: JupyterNotebookFile = None,
                           has_human_input_tool: bool = True,
                           memory: BaseMemory = None,
                           agent_personality: str = 'neutral',
                           fix_imports: bool = True,
                           install_missing_packages: bool = True,
                           fix_bad_calls: bool = True,
                           autofix_mistakes: bool = False,
                           autofix_widget: bool = False,
                           be_didactic: bool = False,
                           verbose: bool = False
                           ) -> AgentExecutor:

    # Get app configuration:
    config = AppConfiguration('omega')

    # Chat callback manager:
    chat_callback_manager = (AsyncCallbackManager(
        [chat_callback_handler]) if is_async else CallbackManager(
        [chat_callback_handler])) if chat_callback_handler else None

    # Tool callback manager:
    tool_callback_manager = (CallbackManager(
        [tool_callback_handler])) if chat_callback_handler else None

    # Basic list of tools:
    tools = [WikipediaQueryTool(callback_manager=tool_callback_manager),
             WebSearchTool(callback_manager=tool_callback_manager),
             PythonFunctionsInfoTool(callback_manager=tool_callback_manager),
             ExceptionCatcherTool(callback_manager=tool_callback_manager),
             # FileDownloadTool(),
             PythonCodeExecutionTool(callback_manager=tool_callback_manager),
             PipInstallTool(callback_manager=tool_callback_manager)]

    # Adding the human input tool if required:
    if has_human_input_tool:
        tools.append(HumanInputTool(callback_manager=tool_callback_manager))

    # Adding napari tools if required:
    if to_napari_queue:

        # Napari tool shared parameters:
        kwargs = {'llm': tool_llm,
                  'to_napari_queue': to_napari_queue,
                  'from_napari_queue': from_napari_queue,
                  'notebook': notebook,
                  'callback_manager': tool_callback_manager,
                  'fix_imports': fix_imports,
                  'install_missing_packages': install_missing_packages,
                  'fix_bad_calls': fix_bad_calls,
                  'verbose': verbose
                  }

        # Adding all napari tools:
        tools.append(NapariViewerControlTool(**kwargs, return_direct=not autofix_mistakes))
        tools.append(NapariViewerQueryTool(**kwargs, return_direct=not autofix_mistakes))
        tools.append(NapariViewerExecutionTool(**kwargs, return_direct=not autofix_mistakes))
        if is_gpt_vision_available():
            tools.append(NapariViewerVisionTool(**kwargs, return_direct=False))
        tools.append(NapariWidgetMakerTool(**kwargs, return_direct=not autofix_widget))
        tools.append(NapariFileOpenTool(**kwargs))
        tools.append(WebImageSearchTool(**kwargs))
        tools.append(CellNucleiSegmentationTool(**kwargs))

        # Future task: remove once Aydin supports Apple Silicon:
        if not is_apple_silicon():
            tools.append(ImageDenoisingTool(**kwargs))

        # Adding all napari plugin tools:
        tool_classes = discover_omega_tools()

        # Filter out the example tool:
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


    # Do this so we can see exactly what's going on under the hood
    from langchain.globals import set_debug
    set_debug(True)

    # prepend the personality:
    PREFIX_ = SYSTEM + PERSONALITY[agent_personality]

    # Create the agent:
    if 'gpt-' in main_llm_model_name:

        # Import OpenAI's functions agent class:
        from napari_chatgpt.omega.omega_agent.OpenAIFunctionsOmegaAgent import \
            OpenAIFunctionsOmegaAgent

        extra_prompt_messages = [MessagesPlaceholder(variable_name="chat_history")]

        # Instantiate the agent:
        agent = OpenAIFunctionsOmegaAgent.from_llm_and_tools(
            llm=main_llm,
            tools=tools,
            system_message=SystemMessage(
                content=PREFIX_
            ),
            # human_message=SUFFIX,
            verbose=verbose,
            callback_manager=chat_callback_manager,
            extra_prompt_messages=extra_prompt_messages,
            be_didactic=be_didactic
        )

    else:

        if be_didactic:
            aprint("Didactic mode not yet supported for non-OpenAI agents. Ignoring.")

        # Import default ReAct Agent class:
        from napari_chatgpt.omega.omega_agent.ConversationalChatOmegaAgent import \
            ConversationalChatOmegaAgent

        # Instantiate the agent:
        agent = ConversationalChatOmegaAgent.from_llm_and_tools(
            llm=main_llm,
            tools=tools,
            PREFIX=PREFIX_,
            SUFFIX=SUFFIX,
            verbose=verbose,
            callback_manager=chat_callback_manager,
        )

    # Create the executor:
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=verbose,
        callback_manager=chat_callback_manager,
        max_iterations=config.get('agent_max_iterations', 5),
        early_stopping_method='generate',
        handle_parsing_errors=config.get('agent_handle_parsing_errors', True),
    )

    return agent_executor
