from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from litemind.agent.tools.callbacks.base_tool_callbacks import BaseToolCallbacks

if TYPE_CHECKING:
    from litemind.agent.tools.base_tool import BaseTool


class OmegaToolCallbacks(BaseToolCallbacks):
    """
    OmegaToolCallbacks is a class that provides callback functionality for tool lifecycle events.
    It inherits from BaseToolCallbacks and implements methods to handle events when a tool starts,
    ends, or encounters an error. This class is designed to allow users to define custom behavior
    for these events by passing in callback functions that will be executed at the appropriate times.
    """

    def __init__(
        self,
        _on_tool_start: Callable,
        _on_tool_activity: Callable,
        _on_tool_end: Callable,
        _on_tool_error: Callable,
    ):
        """
        Initialize the OmegaToolCallbacks with specific callback functions.
        This class is designed to handle tool lifecycle events such as start, activity, end, and error.
        It allows for custom behavior to be defined when these events occur by passing
        callback functions that will be invoked at the appropriate times.

        Parameters
        ----------
        _on_tool_start: Callable
            A callback function to be called when a tool starts.
            It should accept the tool instance and any additional arguments.
        _on_tool_activity: Callable
            A callback function to be called when a tool is active.
            It should accept the tool instance, the type of activity, and any additional keyword arguments.
        _on_tool_end: Callable
            A callback function to be called when a tool ends.
            It should accept the tool instance and the result of the tool execution.
        _on_tool_error: Callable
            A callback function to be called when a tool encounters an error.
            It should accept the tool instance and the exception that occurred.
        """

        self._on_tool_start = _on_tool_start
        self._on_tool_activity = _on_tool_activity
        self._on_tool_end = _on_tool_end
        self._on_tool_error = _on_tool_error

    def on_tool_start(self, tool: "BaseTool", *args, **kwargs) -> None:
        self._on_tool_start(tool, kwargs["query"])

    def on_tool_activity(self, tool: "BaseTool", activity_type: str, **kwargs) -> Any:
        self._on_tool_activity(tool, activity_type, kwargs.get("code", None))

    def on_tool_end(self, tool: "BaseTool", result: Any) -> None:
        self._on_tool_end(tool, result)

    def on_tool_error(self, tool: "BaseTool", exception: Exception) -> None:
        self._on_tool_error(tool, exception)
