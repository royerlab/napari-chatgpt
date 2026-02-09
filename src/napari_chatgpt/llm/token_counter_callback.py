"""Token-counting callback for tracking LLM usage across all API calls."""

from typing import List

from litemind.agent.messages.message import Message
from litemind.apis.callbacks.base_api_callbacks import BaseApiCallbacks


def estimate_tokens(text: str) -> int:
    """Estimate token count from text using a word-based heuristic.

    Uses the approximation: tokens ~ words * 1.3, which is reasonable
    for English text across most tokenizers.

    Parameters
    ----------
    text : str
        The text to estimate tokens for.

    Returns
    -------
    int
        Estimated token count, minimum 1 for non-empty text.
    """
    if not text:
        return 0
    return max(1, int(len(text.split()) * 1.3))


class TokenCounterCallback(BaseApiCallbacks):
    """Counts tokens for every LLM call via on_text_generation.

    This callback is registered on the CombinedApi and fires on every
    text generation call — including internal sub-calls from tools,
    segmentation prompts, code generation, etc.
    """

    def __init__(self):
        self.total_tokens: int = 0

    def on_text_generation(
        self, messages: List[Message], response, **kwargs
    ) -> None:
        """Accumulate estimated tokens for all messages and the response."""
        for m in messages:
            self.total_tokens += estimate_tokens(m.to_plain_text())
        # response can be a single Message or a List[Message]:
        if isinstance(response, list):
            for m in response:
                self.total_tokens += estimate_tokens(m.to_plain_text())
        else:
            self.total_tokens += estimate_tokens(response.to_plain_text())

    def reset(self):
        """Reset the token counter to zero."""
        self.total_tokens = 0
