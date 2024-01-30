from typing import Any, Dict, Union, List

from arbol import aprint
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentFinish, AgentAction, LLMResult
from starlette.websockets import WebSocket

from napari_chatgpt.chat_server.chat_response import ChatResponse
from napari_chatgpt.utils.async_utils.run_async import run_async
from napari_chatgpt.utils.notebook.jupyter_notebook import JupyterNotebookFile


class ToolCallbackHandler(BaseCallbackHandler):
    """Callback handler for tool responses."""

    def __init__(self,
                 websocket: WebSocket,
                 notebook: JupyterNotebookFile,
                 verbose: bool = False):
        self.websocket = websocket
        self.notebook = notebook
        self.verbose = verbose
        self.last_internal_tool_response = None

    async def on_llm_start(
            self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""
        pass

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
        """Run on new LLM token. Only available when streaming is enabled."""
        pass

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        """Run when LLM ends running."""
        pass

    async def on_llm_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when LLM errors."""
        pass

    def on_chain_start(
            self, serialized: Dict[str, Any], inputs: Dict[str, Any],
            **kwargs: Any
    ) -> Any:
        """Run when chain starts running."""
        if self.verbose:
            aprint(
                f"TOOL on_chain_start: serialized={serialized},  inputs={inputs}")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Run when chain ends running."""
        tool_response = outputs['text']
        self.last_internal_tool_response = tool_response
        if self.verbose:
            aprint(f"TOOL on_chain_end: {tool_response}")
        resp = ChatResponse(sender="agent",
                            message=tool_response,
                            type="tool_result")
        run_async(self.websocket.send_json, resp.dict())

        if self.notebook:
            self.notebook.add_markdown_cell("### Omega:\n"+
                                            "Tool response:\n"+
                                            tool_response)


    def on_chain_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when chain errors."""
        if self.verbose:
            aprint(f"TOOL on_chain_error: {error}")

    def on_tool_start(
            self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> Any:
        """Run when tool starts running."""
        if self.verbose:
            aprint(
                f"TOOL on_tool_start: serialized={serialized}, input_str={input_str}")

        self.last_internal_tool_response = None

        # tool = camel_case_to_lower_case(serialized['name'])
        # message = f"The {tool} received this request: '{input_str}'"
        # resp = ChatResponse(sender="agent", message=message, type="tool_start")
        # asyncio.run(self.websocket.send_json(resp.dict()))

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """Run when tool ends running."""
        if self.verbose:
            aprint(f"TOOL on_tool_end: {output}")
        if output.startswith('Error:') or 'Failure' in output:
            resp = ChatResponse(sender="agent", message=output, type="error")
            run_async(self.websocket.send_json, resp.dict())
            if self.notebook:
                self.notebook.add_markdown_cell("### Omega:\n" +
                                                "Error:\n" +
                                                output)
        else:
            resp = ChatResponse(sender="agent", message=output, type="tool_result")
            run_async(self.websocket.send_json, resp.dict())
            if self.notebook:
                self.notebook.add_markdown_cell("### Omega:\n" +
                                                "Tool result:\n" +
                                                output)


    def on_tool_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when tool errors."""
        if self.verbose:
            aprint(f"TOOL on_tool_error: {error}")
        error_type = type(error).__name__
        error_message = ', '.join(error.args)
        message = f"Failed because:\n'{error_message}'\nException: '{error_type}'\n"
        resp = ChatResponse(sender="agent", message=message, type="error")
        run_async(self.websocket.send_json, resp.dict())
        if self.notebook:
            self.notebook.add_markdown_cell("### Omega:\n" +
                                            "Error:\n" +
                                            message)

    def on_text(self, text: str, **kwargs: Any) -> Any:
        """Run on arbitrary text."""
        if self.verbose:
            aprint(f"TOOL on_text: {text}")

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""
        pass

    async def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Run on agent end."""
        pass
