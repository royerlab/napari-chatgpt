"""Data schemas for WebSocket chat messages between the server and web UI."""

from dataclasses import dataclass


@dataclass
class ChatResponse:
    """WebSocket message exchanged between the chat server and the web UI.

    Attributes:
        sender: Origin of the message, either ``"user"`` or ``"agent"``.
        message: The text content of the message.
        type: Message type controlling UI behavior. Values include
            ``"start"``, ``"thinking"``, ``"tool_start"``,
            ``"tool_activity"``, ``"tool_result"``, ``"final"``,
            and ``"error"``.
        tokens: Number of tokens used for this individual response.
        total_tokens: Cumulative token count for the entire session.
    """

    sender: str = ""
    message: str = ""
    type: str = ""
    tokens: int = 0
    total_tokens: int = 0

    def dict(self):
        """Serialize the response to a plain dictionary for JSON transmission."""
        return {
            "sender": self.sender,
            "message": self.message,
            "type": self.type,
            "tokens": self.tokens,
            "total_tokens": self.total_tokens,
        }
