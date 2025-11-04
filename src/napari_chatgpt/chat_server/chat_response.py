"""Schemas for the chat app."""

from dataclasses import dataclass


@dataclass
class ChatResponse:
    """Chat response schema."""

    sender: str = ""
    message: str = ""
    type: str = ""

    def dict(self):
        """
        Return a dictionary representation of the chat response with sender, message, and type fields.
        """
        return {"sender": self.sender, "message": self.message, "type": self.type}
