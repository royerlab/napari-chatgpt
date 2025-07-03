import asyncio
from pprint import pprint
from typing import Any, Dict, Union, List, Optional
from uuid import UUID

from arbol import aprint
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema import AgentFinish, AgentAction, LLMResult, BaseMessage
from starlette.websockets import WebSocket

from napari_chatgpt.chat_server.chat_response import ChatResponse
from napari_chatgpt.utils.notebook.jupyter_notebook import JupyterNotebookFile
from napari_chatgpt.utils.strings.camel_case_to_normal import camel_case_to_lower_case_with_space


class ChatCallbackHandler(AsyncCallbackHandler):
    """Callback handler for chat responses."""

    def __init__(
        self, websocket: WebSocket, notebook: JupyterNotebookFile, verbose: bool = False
    ):
        self.websocket: WebSocket = websocket
        self.notebook: JupyterNotebookFile = notebook
        self.verbose = verbose
        self.last_tool_used = ""
        self.last_tool_input = ""


    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""
        pprint(prompts)
        resp = ChatResponse(sender="agent", message="", type="typing")
        await self.websocket.send_json(resp.dict())



    # TODO:
    async def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when tool errors."""
        if self.verbose:
            aprint(f"CHAT on_tool_error: {error}")
        error_type = type(error).__name__
        error_message = ", ".join(error.args)
        message = f"Failed because:\n'{error_message}'\nException: '{error_type}'\n"
        resp = ChatResponse(sender="agent", message=message, type="error")
        asyncio.run(self.websocket.send_json(resp.dict()))

        if self.notebook:
            self.notebook.add_markdown_cell("### Omega:\n" + "Error:\n" + message)



    async def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""
        if self.verbose:
            aprint(f"CHAT on_agent_action: {action}")
        tool = camel_case_to_lower_case_with_space(action.tool)

        # extract value for args key after checking if action.tool_input is a dict:
        if isinstance(action.tool_input, dict):
            argument = action.tool_input.get("args", "")

            # if argument is a singleton list, unpop that single element:
            if isinstance(argument, list):
                argument = argument[0]

        else:
            argument = action.tool_input

        message = f"I am using the {tool} to tackle your request: '{argument}'"

        self.last_tool_used = tool
        self.last_tool_input = action.tool_input

        # if not parse_command([action.tool],action.log):
        #     message += f"\n {action.log}"

        resp = ChatResponse(sender="agent", message=message, type="action")
        await self.websocket.send_json(resp.dict())

        if self.notebook:
            self.notebook.add_markdown_cell("### Omega:\n" + message)

    async def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Run on agent end."""
        if self.verbose:
            aprint(f"CHAT on_agent_finish: {finish}")
        # message = finish.return_values['output']
        # resp = ChatResponse(sender="agent", message=message, type="finish")
        # await self.websocket.send_json(resp.dict())
