from typing import Any, Dict, Union, List

from arbol import aprint
from langchain.callbacks.base import AsyncCallbackHandler, BaseCallbackHandler
from langchain.schema import AgentFinish, AgentAction, LLMResult

from src.napari_chatgpt.chat_server.chat_response import ChatResponse

class ChatCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming LLM responses."""

    def __init__(self, websocket):
        self.websocket = websocket

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""


    def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
        """Run on new LLM token. Only available when streaming is enabled."""
        # resp = ChatResponse(sender="bot", message=token, type="stream")
        # await self.websocket.send_json(resp.dict())

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        """Run when LLM ends running."""


    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when LLM errors."""


    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> Any:
        """Run when chain starts running."""
        # aprint(f"on_chain_start: serialized={serialized},  inputs={inputs}")


    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Run when chain ends running."""
        # aprint(f"on_chain_end: {outputs}")


    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when chain errors."""
        # aprint(f"on_chain_error: {error}")

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> Any:
        """Run when tool starts running."""
        # aprint(f"on_tool_start: serialized={serialized}, input_str={input_str}")

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """Run when tool ends running."""
        # aprint(f"on_tool_end: {output}")


    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when tool errors."""
        # aprint(f"on_tool_error: {error}")


    def on_text(self, text: str, **kwargs: Any) -> Any:
        """Run on arbitrary text."""
        # aprint(f"on_text: {text}")

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""
        # aprint(f"on_agent_action: {action}")

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Run on agent end."""
        # aprint(f"on_agent_finish: {finish}")