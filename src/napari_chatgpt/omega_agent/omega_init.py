from queue import Queue

from arbol import aprint, asection
from litemind.agent.agent import Agent
from litemind.agent.messages.message import Message
from litemind.agent.tools.callbacks.base_tool_callbacks import BaseToolCallbacks
from litemind.agent.tools.toolset import ToolSet
from litemind.apis.model_features import ModelFeatures

from napari_chatgpt.llm.litemind_api import (
    get_litemind_api,
    get_llm,
    has_model_support_for,
)
from napari_chatgpt.omega_agent.omega_agent import OmegaAgent
from napari_chatgpt.omega_agent.prompts import DIDACTICS, PERSONALITY, SYSTEM
from napari_chatgpt.utils.configuration.app_configuration import AppConfiguration
from napari_chatgpt.utils.notebook.jupyter_notebook import JupyterNotebookFile


def initialize_omega_agent(
    to_napari_queue: Queue = None,
    from_napari_queue: Queue = None,
    main_llm_model_name: str = None,
    tool_llm_model_name: str = None,
    temperature: float = 0.0,
    tool_temperature: float = 0.0,
    has_builtin_websearch_tool: bool = True,
    notebook: JupyterNotebookFile = None,
    agent_personality: str = "neutral",
    fix_imports: bool = True,
    install_missing_packages: bool = True,
    fix_bad_calls: bool = True,
    autofix_mistakes: bool = False,
    autofix_widget: bool = False,
    be_didactic: bool = False,
    tool_callbacks: BaseToolCallbacks | None = None,
    verbose: bool = False,
) -> Agent:
    with asection("Initialising Omega Agent"):
        # Get app configuration:
        config = AppConfiguration("omega")

        # get the LLM for tools:
        tool_llm = get_llm(model_name=tool_llm_model_name, temperature=tool_temperature)

        # tool context:
        tool_context = {
            "llm": tool_llm,
            "to_napari_queue": to_napari_queue,
            "from_napari_queue": from_napari_queue,
            "notebook": notebook,
            "fix_imports": fix_imports,
            "install_missing_packages": install_missing_packages,
            "fix_bad_calls": fix_bad_calls,
            "autofix_mistakes": autofix_mistakes,
            "autofix_widget": autofix_widget,
            "verbose": verbose,
            "callback": None,  # This will be set later
        }

        toolset: ToolSet = prepare_toolset(tool_context, main_llm_model_name)

        # Add built-in web search tool if required:
        if has_builtin_websearch_tool:
            if has_model_support_for(
                main_llm_model_name, [ModelFeatures.WebSearchTool]
            ):
                aprint("Builtin websearch tool has been added to Omega.")
                toolset.add_builtin_web_search_tool()
            else:
                aprint(
                    f"Model '{main_llm_model_name}' does not support the web search tool."
                )

        # Add tool callbacks:
        toolset.add_tool_callback(tool_callbacks)

        # Get the LiteMind API:
        api = get_litemind_api()

        # Get the main LLM:
        omega_agent = OmegaAgent(
            api=api,
            name="Omega",
            model_name=main_llm_model_name,
            temperature=temperature,
            toolset=toolset,
        )

        # Format system instructions:
        system_message = Message(role="system")
        system_message.append_templated_text(
            SYSTEM,
            personality=PERSONALITY[agent_personality],
            didactics=DIDACTICS if be_didactic else "",
        )
        with asection("System Prompt:"):
            aprint(str(system_message))

        # Append system instructions:
        omega_agent.append_system_message(system_message)

        # Return agent
        return omega_agent


def prepare_toolset(tool_context, vision_llm_model_name) -> ToolSet:
    tools = []

    # Adding all napari tools:
    _append_all_napari_tools(tool_context, tools, vision_llm_model_name)

    # Create Toolset from the list of tools:
    toolset = ToolSet(tools)

    return toolset


def _append_all_napari_tools(tool_context, tools, vision_llm_model_name):
    from napari_chatgpt.omega_agent.tools.napari.viewer_control_tool import (
        NapariViewerControlTool,
    )

    tools.append(NapariViewerControlTool(**tool_context))

    from napari_chatgpt.omega_agent.tools.napari.viewer_execution_tool import (
        NapariViewerExecutionTool,
    )

    tools.append(NapariViewerExecutionTool(**tool_context))

    from napari_chatgpt.omega_agent.tools.napari.viewer_query_tool import (
        NapariViewerQueryTool,
    )

    tools.append(NapariViewerQueryTool(**tool_context))

    from napari_chatgpt.omega_agent.tools.napari.widget_maker_tool import (
        NapariWidgetMakerTool,
    )

    tools.append(NapariWidgetMakerTool(**tool_context))

    from napari_chatgpt.omega_agent.tools.napari.file_open_tool import (
        NapariFileOpenTool,
    )

    tools.append(NapariFileOpenTool(**tool_context))

    from napari_chatgpt.omega_agent.tools.search.web_image_search_tool import (
        WebImageSearchTool,
    )

    tools.append(WebImageSearchTool(**tool_context))

    from napari_chatgpt.omega_agent.tools.napari.cell_nuclei_segmentation_tool import (
        CellNucleiSegmentationTool,
    )

    tools.append(CellNucleiSegmentationTool(**tool_context))

    from napari_chatgpt.utils.llm.vision import is_vision_available

    if is_vision_available():
        from napari_chatgpt.omega_agent.tools.napari.viewer_vision_tool import (
            NapariViewerVisionTool,
        )

        tools.append(
            NapariViewerVisionTool(
                vision_model_name=vision_llm_model_name, **tool_context
            )
        )

    from napari_chatgpt.utils.system.is_apple_silicon import is_apple_silicon

    # Future task: remove once Aydin supports Apple Silicon:
    if not is_apple_silicon():
        from napari_chatgpt.omega_agent.tools.napari.image_denoising_tool import (
            ImageDenoisingTool,
        )

        tools.append(ImageDenoisingTool(**tool_context))


def _append_basic_tools(tool_context, tools):
    from napari_chatgpt.omega_agent.tools.search.web_search_tool import WebSearchTool
    from napari_chatgpt.omega_agent.tools.special.exception_catcher_tool import (
        ExceptionCatcherTool,
    )
    from napari_chatgpt.omega_agent.tools.special.functions_info_tool import (
        PythonFunctionsInfoTool,
    )
    from napari_chatgpt.omega_agent.tools.special.package_info_tool import (
        PythonPackageInfoTool,
    )
    from napari_chatgpt.omega_agent.tools.special.pip_install_tool import PipInstallTool
    from napari_chatgpt.omega_agent.tools.special.python_repl import (
        PythonCodeExecutionTool,
    )

    tools.append(WebSearchTool(**tool_context))
    tools.append(PythonFunctionsInfoTool(**tool_context))
    tools.append(ExceptionCatcherTool(**tool_context))
    # tools.append(FileDownloadTool(**tool_context))
    tools.append(PythonCodeExecutionTool(**tool_context))
    tools.append(PythonPackageInfoTool(**tool_context))
    tools.append(PipInstallTool(**tool_context))
