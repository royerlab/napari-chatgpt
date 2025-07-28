from typing import Any, Callable

from litemind.agent.tools.callbacks.base_tool_callbacks import BaseToolCallbacks


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
        Initialize OmegaToolCallbacks with user-defined callbacks for tool lifecycle events.
        
        This constructor stores the provided callback functions, which are invoked during tool start, activity, end, and error events to enable custom handling of each stage.
        """

        self._on_tool_start = _on_tool_start
        self._on_tool_activity = _on_tool_activity
        self._on_tool_end = _on_tool_end
        self._on_tool_error = _on_tool_error

    def on_tool_start(self, tool: "BaseTool", *args, **kwargs) -> None:
        """
        Invoke the start callback for a tool, passing the tool instance and the associated query.
        
        Parameters:
            tool (BaseTool): The tool instance for which the start event is triggered.
        """
        self._on_tool_start(tool, kwargs["query"])

    def on_tool_activity(self, tool: "BaseTool", activity_type: str, **kwargs) -> Any:
        """
        Invoke the activity callback for a tool with the specified activity type and optional code.
        
        Parameters:
            activity_type (str): The type of activity occurring.
            code (Any, optional): An optional code associated with the activity, if provided.
        
        Returns:
            Any: The result returned by the activity callback.
        """
        self._on_tool_activity(tool, activity_type, kwargs.get("code", None))

    def on_tool_end(self, tool: "BaseTool", result: Any) -> None:
        """
        Invoke the end callback when a tool finishes execution.
        
        Parameters:
            tool (BaseTool): The tool instance that has completed execution.
            result (Any): The result produced by the tool.
        """
        self._on_tool_end(tool, result)

    def on_tool_error(self, tool: "BaseTool", exception: Exception) -> None:
        """
        Invoke the error callback when a tool encounters an exception.
        
        Parameters:
            tool (BaseTool): The tool instance that raised the exception.
            exception (Exception): The exception encountered during tool execution.
        """
        self._on_tool_error(tool, exception)
