from typing import Any, Dict, List, Union

from arbol import aprint
from colorama import Fore
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult


class ToolCallbackHandler(BaseCallbackHandler):
    """Custom CallbackHandler."""

    def __init__(self, tool_name: str):
        self.tool_name = tool_name

    def on_llm_start(
            self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Print out the prompts."""
        pass

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Do nothing."""
        pass

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Do nothing."""
        pass

    def on_llm_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Do nothing."""
        pass

    def on_chain_start(
            self, serialized: Dict[str, Any], inputs: Dict[str, Any],
            **kwargs: Any
    ) -> None:
        """Print out that we are entering a chain."""
        aprint(Fore.RED + f"Entering tool {self.tool_name} chain:")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Print out that we finished a chain."""
        aprint(Fore.RED + f"Leaving tool {self.tool_name} chain.")

    def on_chain_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Do nothing."""
        pass
