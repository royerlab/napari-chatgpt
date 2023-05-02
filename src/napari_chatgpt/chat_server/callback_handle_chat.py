import asyncio
from typing import Any, Dict, Union, List

from arbol import aprint
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema import AgentFinish, AgentAction, LLMResult

from napari_chatgpt.chat_server.chat_response import ChatResponse
from napari_chatgpt.utils.camel_case_to_normal import camel_case_to_lower_case


class ChatCallbackHandler(AsyncCallbackHandler):
    """Callback handler for chat responses."""

    def __init__(self, websocket):
        self.websocket = websocket

    async def on_llm_start(
            self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""
        resp = ChatResponse(sender="agent", message='', type="typing")
        await self.websocket.send_json(resp.dict())

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
        """Run on new LLM token. Only available when streaming is enabled."""

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        """Run when LLM ends running."""

    async def on_llm_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when LLM errors."""

    async def on_chain_start(
            self, serialized: Dict[str, Any], inputs: Dict[str, Any],
            **kwargs: Any
    ) -> Any:
        """Run when chain starts running."""
        aprint(
            f"CHAT on_chain_start: serialized={serialized},  inputs={inputs}")

    async def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Run when chain ends running."""
        aprint(f"CHAT on_chain_end: {outputs}")

    async def on_chain_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when chain errors."""
        aprint(f"CHAT on_chain_error: {error}")

    async def on_tool_start(
            self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> Any:
        """Run when tool starts running."""
        aprint(
            f"CHAT on_tool_start: serialized={serialized}, input_str={input_str}")

    async def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """Run when tool ends running."""
        aprint(f"CHAT on_tool_end: output={output}")

    async def on_tool_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when tool errors."""
        aprint(f"CHAT on_tool_error: {error}")
        error_type = type(error).__name__
        error_message = ', '.join(error.args)
        message = f"Failed because:\n'{error_message}'\nException: '{error_type}'\n"
        resp = ChatResponse(sender="agent", message=message, type="error")
        asyncio.run(self.websocket.send_json(resp.dict()))

    async def on_text(self, text: str, **kwargs: Any) -> Any:
        """Run on arbitrary text."""
        pass
        aprint(f"CHAT on_text: {text}")

    async def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""
        aprint(f"CHAT on_agent_action: {action}")
        tool = camel_case_to_lower_case(action.tool)
        message = f"I am using the {tool} to tackle your request: '{action.tool_input}'"

        if not 'Action:' in action.log and not 'Input:' in action.log:
            message += f"\n {action.log}"

        resp = ChatResponse(sender="agent", message=message, type="action")
        await self.websocket.send_json(resp.dict())

    async def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Run on agent end."""
        aprint(f"CHAT on_agent_finish: {finish}")
        # message = finish.return_values['output']
        # resp = ChatResponse(sender="agent", message=message, type="finish")
        # await self.websocket.send_json(resp.dict())
