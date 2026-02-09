"""Schemas for the chat app."""

from dataclasses import dataclass


@dataclass
class ChatResponse:
    """Chat response schema."""

    sender: str = ""
    message: str = ""
    type: str = ""
    tokens: int = 0
    total_tokens: int = 0

    def dict(self):
        return {
            "sender": self.sender,
            "message": self.message,
            "type": self.type,
            "tokens": self.tokens,
            "total_tokens": self.total_tokens,
        }
