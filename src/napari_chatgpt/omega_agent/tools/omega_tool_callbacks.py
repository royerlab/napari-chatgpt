"""Callback adapter for Omega tool lifecycle events.

Provides ``OmegaToolCallbacks``, which translates LiteMind's
``BaseToolCallbacks`` interface into simple user-supplied callables so
that the chat UI can react to tool start, activity, end, and error
events without depending on LiteMind internals.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from litemind.agent.tools.callbacks.base_tool_callbacks import BaseToolCallbacks

if TYPE_CHECKING:
    from litemind.agent.tools.base_tool import BaseTool


class OmegaToolCallbacks(BaseToolCallbacks):
    """Delegates LiteMind tool lifecycle events to user-supplied callables.

    Each callback is a plain function passed at construction time, making
    it easy to wire tool events into the Qt-based chat UI without
    subclassing.
    """

    def __init__(
        self,
        _on_tool_start: Callable,
        _on_tool_activity: Callable,
        _on_tool_end: Callable,
        _on_tool_error: Callable,
    ):
        """Initialise with four lifecycle callback functions.

        Args:
            _on_tool_start: Called when a tool begins execution.
                Signature: ``(tool, query) -> None``.
            _on_tool_activity: Called during tool activity (e.g. code
                generation). Signature:
                ``(tool, activity_type, code_or_none) -> Any``.
            _on_tool_end: Called when a tool finishes successfully.
                Signature: ``(tool, result) -> None``.
            _on_tool_error: Called when a tool raises an exception.
                Signature: ``(tool, exception) -> None``.
        """

        self._on_tool_start = _on_tool_start
        self._on_tool_activity = _on_tool_activity
        self._on_tool_end = _on_tool_end
        self._on_tool_error = _on_tool_error

    def on_tool_start(self, tool: "BaseTool", *args, **kwargs) -> None:
        """Dispatch the tool-start event to the user callback."""
        self._on_tool_start(tool, kwargs["query"])

    def on_tool_activity(self, tool: "BaseTool", activity_type: str, **kwargs) -> Any:
        """Dispatch a tool-activity event (e.g. code generation) to the user callback."""
        self._on_tool_activity(tool, activity_type, kwargs.get("code", None))

    def on_tool_end(self, tool: "BaseTool", result: Any) -> None:
        """Dispatch the tool-end event to the user callback."""
        self._on_tool_end(tool, result)

    def on_tool_error(self, tool: "BaseTool", exception: Exception) -> None:
        """Dispatch the tool-error event to the user callback."""
        self._on_tool_error(tool, exception)
