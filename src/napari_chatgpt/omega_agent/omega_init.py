"""Factory functions for initialising the Omega agent and its toolset.

This module wires together the LLM backend, system prompt, tools, and
napari communication queues to produce a fully configured ``OmegaAgent``
ready to handle user conversations.
"""

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
    be_didactic: bool = False,
    tool_callbacks: BaseToolCallbacks | None = None,
    verbose: bool = False,
) -> Agent:
    """Build and return a fully configured Omega agent.

    This is the main entry point for agent initialisation. It creates
    the tool LLM, assembles the toolset, attaches the system prompt
    (including personality and optional didactic mode), and returns the
    ready-to-use ``OmegaAgent``.

    Args:
        to_napari_queue: Queue for sending callables to the napari Qt
            thread.
        from_napari_queue: Queue for receiving results from the napari
            Qt thread.
        main_llm_model_name: Model identifier for the main agent LLM.
        tool_llm_model_name: Model identifier for the tool sub-LLM
            used for code generation.
        temperature: Sampling temperature for the main agent LLM.
        tool_temperature: Sampling temperature for the tool sub-LLM.
        has_builtin_websearch_tool: Whether to add a built-in web
            search tool (if the model supports it).
        notebook: Optional Jupyter notebook to record generated code.
        agent_personality: Personality key (see ``prompts.PERSONALITY``).
        be_didactic: If ``True``, include didactic instructions in the
            system prompt.
        tool_callbacks: Optional callbacks for tool lifecycle events.
        verbose: Enable verbose logging in tools.

    Returns:
        A configured ``OmegaAgent`` instance.

    Raises:
        ValueError: If either queue argument is ``None``.
    """
    if to_napari_queue is None or from_napari_queue is None:
        raise ValueError("to_napari_queue and from_napari_queue must not be None")

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
    """Create a ``ToolSet`` containing all built-in and external tools.

    Args:
        tool_context: Dictionary of shared context passed to each tool
            constructor (queues, LLM, notebook, etc.).
        vision_llm_model_name: Model name used for the vision tool.

    Returns:
        A ``ToolSet`` populated with all discovered tools.
    """
    tools = []

    # Adding all tools:
    _append_all_tools(tool_context, tools, vision_llm_model_name)

    # Discover and add external tools via entry points:
    _discover_external_tools(tool_context, tools)

    # Create Toolset from the list of tools:
    toolset = ToolSet(tools)

    return toolset


def _append_all_tools(tool_context, tools, vision_llm_model_name):
    """Instantiate all built-in Omega tools and append them to *tools*.

    Conditionally includes vision and denoising tools based on runtime
    availability of their dependencies.

    Args:
        tool_context: Shared context dictionary forwarded to each tool.
        tools: Mutable list to which new tool instances are appended.
        vision_llm_model_name: Model name passed to the vision tool.
    """
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

    from napari_chatgpt.omega_agent.tools.napari.napari_plugin_tool import (
        NapariPluginTool,
    )

    tools.append(NapariPluginTool(**tool_context))

    from napari_chatgpt.omega_agent.tools.napari.layer_action_tool import (
        NapariLayerActionTool,
    )

    tools.append(NapariLayerActionTool(**tool_context))

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

    from napari_chatgpt.omega_agent.tools.napari.image_denoising_tool import (
        _aydin_available,
    )

    if _aydin_available():
        from napari_chatgpt.omega_agent.tools.napari.image_denoising_tool import (
            ImageDenoisingTool,
        )

        tools.append(ImageDenoisingTool(**tool_context))

    from napari_chatgpt.omega_agent.tools.special.file_download_tool import (
        FileDownloadTool,
    )

    tools.append(FileDownloadTool(**tool_context))

    from napari_chatgpt.omega_agent.tools.special.exception_catcher_tool import (
        ExceptionCatcherTool,
    )

    tools.append(ExceptionCatcherTool(**tool_context))

    from napari_chatgpt.omega_agent.tools.special.functions_info_tool import (
        PythonFunctionsInfoTool,
    )

    tools.append(PythonFunctionsInfoTool(**tool_context))

    from napari_chatgpt.omega_agent.tools.special.package_info_tool import (
        PythonPackageInfoTool,
    )

    tools.append(PythonPackageInfoTool(**tool_context))

    from napari_chatgpt.omega_agent.tools.special.pip_install_tool import (
        PipInstallTool,
    )

    tools.append(PipInstallTool(**tool_context))


def _discover_external_tools(tool_context: dict, tools: list) -> None:
    """Discover and instantiate tools registered via entry points.

    External packages can register tools by adding an entry point in
    their ``pyproject.toml``::

        [project.entry-points."napari_chatgpt.tools"]
        my_tool = "my_package:MyToolClass"

    Each entry point must resolve to a class that subclasses
    ``BaseOmegaTool``. Invalid entries are logged and skipped.
    """
    import importlib.metadata

    from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool

    try:
        eps = importlib.metadata.entry_points(group="napari_chatgpt.tools")
    except TypeError:
        # Python 3.9 compatibility: entry_points() doesn't accept group=
        eps = importlib.metadata.entry_points().get("napari_chatgpt.tools", [])

    for ep in eps:
        try:
            tool_class = ep.load()
            if not (
                isinstance(tool_class, type) and issubclass(tool_class, BaseOmegaTool)
            ):
                aprint(
                    f"Skipping entry point '{ep.name}': "
                    f"{tool_class} is not a subclass of BaseOmegaTool"
                )
                continue
            tool_instance = tool_class(**tool_context)
            tools.append(tool_instance)
            aprint(f"Registered external tool: {ep.name} ({tool_class.__name__})")
        except Exception as e:
            aprint(f"Failed to load external tool '{ep.name}': {e}")
