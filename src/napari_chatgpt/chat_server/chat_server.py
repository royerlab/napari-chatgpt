"""FastAPI WebSocket chat server bridging the Omega LLM agent and napari.

This module provides :class:`NapariChatServer`, which exposes a web-based
chat UI over WebSocket. User messages are routed to the Omega agent, which
can inspect and manipulate the napari viewer through the
:class:`~napari_chatgpt.omega_agent.napari_bridge.NapariBridge`.  Tool
activity, errors, and final responses are streamed back to the browser in
real time.
"""

import asyncio
import os
import traceback
import webbrowser
from contextlib import asynccontextmanager
from threading import Thread
from time import sleep
from typing import Any

import napari
from arbol import aprint, asection
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from litemind.agent.messages.message import Message
from litemind.agent.tools.base_tool import BaseTool
from litemind.media.types.media_text import Text
from qtpy.QtCore import QTimer
from starlette.staticfiles import StaticFiles
from uvicorn import Config, Server

from napari_chatgpt.chat_server.chat_response import ChatResponse
from napari_chatgpt.llm.token_counter_callback import TokenCounterCallback
from napari_chatgpt.omega_agent.napari_bridge import NapariBridge, _set_viewer_info
from napari_chatgpt.omega_agent.omega_init import initialize_omega_agent
from napari_chatgpt.omega_agent.tools.omega_tool_callbacks import OmegaToolCallbacks
from napari_chatgpt.utils.configuration.app_configuration import AppConfiguration
from napari_chatgpt.utils.network.port_available import find_first_port_available
from napari_chatgpt.utils.notebook.jupyter_notebook import JupyterNotebookFile
from napari_chatgpt.utils.strings.camel_case_to_normal import (
    camel_case_to_lower_case_with_space,
)


class NapariChatServer:
    """
    A chat server that allows users to interact with a napari viewer
    through a web interface, using Omega Agent to process requests and
    perform actions in the napari environment.
    This server uses FastAPI to handle WebSocket connections and
    provides a real-time chat interface for users to communicate with
    the Omega Agent.
    """

    def __init__(
        self,
        notebook: JupyterNotebookFile,
        napari_bridge: NapariBridge,
        main_llm_model_name: str = None,
        tool_llm_model_name: str = None,
        temperature: float = 0.01,
        tool_temperature: float = 0.01,
        has_builtin_websearch_tool: bool = True,
        memory_type: str = "standard",
        agent_personality: str = "neutral",
        be_didactic: bool = False,
        verbose: bool = False,
    ):
        """Initialize the chat server and register FastAPI routes.

        Args:
            notebook: Jupyter notebook for persisting chat history and
                viewer snapshots. May be ``None`` to disable logging.
            napari_bridge: Thread-safe bridge for communicating with the
                napari viewer.
            main_llm_model_name: Model name for the main Omega agent LLM.
            tool_llm_model_name: Model name for tool-specific LLM calls.
            temperature: Sampling temperature for the main LLM.
            tool_temperature: Sampling temperature for tool LLM calls.
            has_builtin_websearch_tool: Whether to enable the built-in
                web search tool.
            memory_type: Conversation memory strategy
                (e.g. ``"standard"``).
            agent_personality: Personality preset for the Omega agent.
            be_didactic: If True, the agent provides more explanatory
                responses.
            verbose: Enable verbose logging.
        """

        # Flag to keep server running, or stop it:
        self.running = False
        self.uvicorn_server = None
        self.server_thread = None

        # Notebook:
        self.notebook: JupyterNotebookFile = notebook

        # Napari bridge:
        self.napari_bridge: NapariBridge = napari_bridge

        # UV event loop:
        self.event_loop = None

        # Define lifespan context manager for FastAPI:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup: nothing needed currently
            yield
            # Shutdown: nothing needed currently (handled by stop() method)

        # Instantiate FastAPI with lifespan:
        self.app = FastAPI(lifespan=lifespan)

        # Get configuration
        config = AppConfiguration("omega")

        # check if default port is available, if not increment by one until available:
        default_port = config.get("port", 9000)

        # find first available port:
        self.port = find_first_port_available(default_port, default_port + 1000)
        aprint(f"Using port: {self.port}")

        # Mount static files:
        static_files_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "static"
        )
        self.app.mount(
            "/static", StaticFiles(directory=static_files_path), name="static"
        )

        # Load templates:
        templates_files_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "templates"
        )

        # Load Jinja2 templates:
        templates = Jinja2Templates(directory=templates_files_path)

        # Default path:
        @self.app.get("/")
        async def get(request: Request):
            return templates.TemplateResponse(
                "index.html", {"request": request, "port": self.port}
            )

        # Chat path:
        @self.app.websocket("/chat")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()

            # Get the event event_loop:
            self.event_loop = asyncio.get_event_loop()

            # restart a notebook:
            if self.notebook:
                self.notebook.restart()

            # Token counter callback:
            token_counter = TokenCounterCallback()

            # Register token counter on the LiteMind API:
            from napari_chatgpt.llm.litemind_api import get_litemind_api

            api = get_litemind_api()
            api.callback_manager.add_callback(token_counter)

            # Tool's callbacks:
            tool_callbacks = OmegaToolCallbacks(
                _on_tool_start=(
                    lambda t, q: notify_user_omega_tool_start(websocket, t, q)
                ),
                _on_tool_activity=(
                    lambda t, at, c: notify_user_omega_tool_activity(
                        websocket, t, at, c
                    )
                ),
                _on_tool_end=(lambda t, r: notify_user_omega_tool_end(websocket, t, r)),
                _on_tool_error=(lambda t, e: notify_user_omega_error(websocket, e)),
            )

            # Agent
            agent = initialize_omega_agent(
                to_napari_queue=napari_bridge.to_napari_queue,
                from_napari_queue=napari_bridge.from_napari_queue,
                main_llm_model_name=main_llm_model_name,
                tool_llm_model_name=tool_llm_model_name,
                temperature=temperature,
                tool_temperature=tool_temperature,
                has_builtin_websearch_tool=has_builtin_websearch_tool,
                notebook=self.notebook,
                agent_personality=agent_personality,
                be_didactic=be_didactic,
                tool_callbacks=tool_callbacks,
                verbose=verbose,
            )

            dialog_counter = 0

            # Dialog Loop:
            try:
                while True:
                    with asection(f"Dialog iteration {dialog_counter}:"):
                        try:
                            aprint(f"Waiting for user input...")

                            # Receive and send back the client message
                            prompt = await receive_from_user(websocket)

                            with asection(f"User prompt:"):
                                aprint(prompt)

                            if self.notebook:
                                self.notebook.add_markdown_cell("### User:\n" + prompt)

                            # get napari viewer info::
                            viewer_info = self.napari_bridge.get_viewer_info()
                            _set_viewer_info(viewer_info)

                            # call LLM:
                            await notify_user_omega_thinking(websocket)
                            # result = agent(prompt)
                            result = await self.async_run_in_executor(agent, prompt)

                            with asection(f"Agent response:"):
                                # Extract text from result:
                                for i, message in enumerate(result):
                                    with asection(f"Message Block #{i}"):
                                        aprint(message.to_plain_text())

                            await send_final_response_to_user(
                                result, websocket, token_counter
                            )

                            if self.notebook:
                                # Add agent response to notebook:
                                self.notebook.add_markdown_cell(
                                    f"### Omega:\n {result}"
                                )

                                # Add snapshot to notebook:
                                self.notebook.take_snapshot()

                                # write notebook:
                                self.notebook.write()

                        except WebSocketDisconnect:
                            aprint("websocket disconnect")
                            break

                        except Exception as e:
                            traceback.print_exc()
                            resp = ChatResponse(
                                sender="agent",
                                message=f"Sorry, something went wrong ({type(e).__name__}: {str(e)}).",
                                type="error",
                            )
                            await websocket.send_json(resp.dict())
                    dialog_counter += 1
            finally:
                api.callback_manager.remove_callback(token_counter)

        async def receive_from_user(websocket: WebSocket) -> str:
            """Receive a user message, echo it back, and send a start marker."""
            # Receive a question from the user via WebSocket:
            question = await websocket.receive_text()

            # Format the question as a ChatResponse:
            resp = ChatResponse(sender="user", message=question)

            # Send the question back to the web UI via WebSocket:
            await websocket.send_json(resp.dict())

            # Initiates a response -- empty for now:
            start_resp = ChatResponse(sender="agent", type="start")

            # Send the this empty 'place-holder'  response to the user via WebSocket:
            await websocket.send_json(start_resp.dict())

            # Return the question for further processing:
            return question

        async def send_final_response_to_user(
            result: list[Message],
            websocket: WebSocket,
            token_counter: TokenCounterCallback,
        ):
            """Send the agent's final text response and token count to the UI."""
            # Filter out non-text messages:
            text_result = [m for m in result if m.has(Text)]

            # Extract the last message from the result:
            message_str = "\n\n".join([m.to_plain_text() for m in text_result])

            # finalise agent response:
            end_resp = ChatResponse(
                sender="agent",
                message=message_str,
                type="final",
                total_tokens=token_counter.total_tokens,
            )

            # Send the response to the user via WebSocket:
            await websocket.send_json(end_resp.dict())

        async def notify_user_omega_thinking(websocket: WebSocket):
            """Notify user that Omega is thinking."""

            # Format the response as a typing indicator:
            resp = ChatResponse(sender="agent", message="", type="thinking")

            # Send the typing response to the user via WebSocket:
            await websocket.send_json(resp.dict())

        def notify_user_omega_tool_start(
            websocket: WebSocket, tool: BaseTool, query: str
        ):
            """Notify user that Omega started using a tool."""

            # Convert name of the tool to a human-readable format:
            tool_name = camel_case_to_lower_case_with_space(tool.name)

            # Format the message to notify the user:
            message = f"I am using the {tool_name} to tackle your request:\n {query}"

            # Create a ChatResponse object to send to the user:
            resp = ChatResponse(sender="agent", message=message, type="tool_start")

            # Send the message to the user via WebSocket:
            self.sync_handler(websocket.send_json, resp.dict())
            aprint(f"Sent to user via web-ui: {message}")

            # If notebook is available, add the message to it:
            if self.notebook:
                self.notebook.add_markdown_cell("### Omega:\n" + message)

        def notify_user_omega_tool_activity(
            websocket: WebSocket, tool: BaseTool, activity_type: str, code: str
        ):
            """Notify user of tool activity (e.g. code generation and execution)."""
            aprint(f"Tool {tool.name} is {activity_type}...")
            if activity_type == "coding":
                # Convert name of the tool to a human-readable format:
                tool_name = camel_case_to_lower_case_with_space(tool.name)

                # Format the message to notify the user:
                message = f"Tool {tool_name} wrote and executed successfully the following code:\n\n```python\n{code.strip() if code else '[code missing!]'}\n```\n"

                # Create a ChatResponse object to send to the user:
                resp = ChatResponse(
                    sender="agent", message=message, type="tool_activity"
                )

                # Send the message to the user via WebSocket:
                self.sync_handler(websocket.send_json, resp.dict())
                aprint(f"Sent to user via web-ui: {message}")

            else:
                # If activity type is not 'coding' then we raise an error:
                raise ValueError(
                    f"Unknown activity type: {activity_type}. Expected 'coding'."
                )

        def notify_user_omega_tool_end(
            websocket: WebSocket, tool: BaseTool, result: Any
        ):
            """Notify user that Omega's tool usage ended."""

            # Convert to string if result is not a string:
            message = str(result)

            # Create a ChatResponse object to send to the user:
            resp = ChatResponse(sender="agent", message=message, type="tool_result")

            # Send the message to the user via WebSocket:
            self.sync_handler(websocket.send_json, resp.dict())
            aprint(f"Sent to user via web-ui: {message}")

            # If notebook is available, add the message to it:
            if self.notebook:
                self.notebook.add_markdown_cell("### Omega:\n" + message)

        def notify_user_omega_error(websocket: WebSocket, error: Exception):
            """Notify user that Omega's tool encountered an error."""

            # Get the type and message of the error:
            error_type = type(error).__name__
            error_message = ", ".join(str(a) for a in error.args)

            # Format the error message:
            message = f"Failed because:\n'{error_message}'\nException: '{error_type}'\n"

            # Format the response for sending to the user:
            resp = ChatResponse(sender="agent", message=message, type="error")

            # Send the error response to the user via WebSocket:
            self.sync_handler(websocket.send_json, resp.dict())
            aprint(f"Sent to user via web-ui: {message}")

            # If notebook is available, add the error message to it:
            if self.notebook:
                self.notebook.add_markdown_cell("### Omega:\n" + "Error:\n" + message)

    def _start_uvicorn_server(self, app):
        """Start the Uvicorn ASGI server on the configured port (blocking)."""
        with asection(f"Starting Uvicorn server on port {self.port}"):
            config = Config(app, port=self.port)
            self.uvicorn_server = Server(config=config)
            self.running = True
            self.uvicorn_server.run()

    def run(self):
        """Run the chat server (blocking) on the current thread."""
        self._start_uvicorn_server(self.app)

    def stop(self):
        """Gracefully stop the server, napari bridge, and background thread."""
        with asection("Stopping Omega server"):
            self.running = False

            # Stop the napari bridge worker:
            if self.napari_bridge:
                self.napari_bridge.stop()

            # Stop the Uvicorn server:
            if self.uvicorn_server:
                self.uvicorn_server.should_exit = True
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=5)
                if self.server_thread.is_alive():
                    aprint("Warning: Server thread did not stop gracefully")
            aprint("Omega server stopped!")

    def sync_handler(self, _callable, *args, **kwargs):
        """Schedule an async callable from a synchronous (executor) thread.

        Uses ``run_coroutine_threadsafe`` -- the thread-safe counterpart
        of ``create_task`` -- to dispatch the coroutine onto the server's
        event loop.
        """
        asyncio.run_coroutine_threadsafe(_callable(*args, **kwargs), self.event_loop)

    def async_run_in_executor(self, func, *args):
        """Run a blocking function in the default executor.

        Returns an awaitable future so that blocking agent calls do not
        stall the asyncio event loop.
        """
        return self.event_loop.run_in_executor(None, func, *args)


def start_chat_server(
    viewer: napari.Viewer = None,
    main_llm_model_name: str = None,
    tool_llm_model_name: str = None,
    temperature: float = 0.01,
    tool_temperature: float = 0.01,
    has_builtin_websearch_tool: bool = True,
    memory_type: str = "standard",
    agent_personality: str = "neutral",
    be_didactic: bool = False,
    save_chats_as_notebooks: bool = False,
    verbose: bool = False,
):
    """Start the Omega chat server in a background daemon thread.

    Creates a napari viewer (if not provided), sets up the
    :class:`NapariBridge`, and launches the FastAPI WebSocket server.
    Optionally opens the chat UI in the default browser.

    Args:
        viewer: Existing napari viewer instance. A new viewer is
            created when ``None``.
        main_llm_model_name: Model name for the main Omega agent.
        tool_llm_model_name: Model name for tool LLM calls.
        temperature: Sampling temperature for the main LLM.
        tool_temperature: Sampling temperature for tool LLM calls.
        has_builtin_websearch_tool: Enable the built-in web search tool.
        memory_type: Conversation memory strategy.
        agent_personality: Personality preset for the agent.
        be_didactic: If True, agent gives more explanatory answers.
        save_chats_as_notebooks: Persist chat sessions as Jupyter
            notebooks.
        verbose: Enable verbose logging.

    Returns:
        The running :class:`NapariChatServer` instance.
    """
    with asection("Starting chat server"):

        # get configuration:
        config = AppConfiguration("omega")

        # Instantiates napari viewer if needed:
        if not viewer:
            viewer = napari.Viewer()

        # Instantiates a notebook:
        notebook_folder_path = config.get("notebook_path")
        aprint(f"Using notebook folder path: {notebook_folder_path}")
        notebook = (
            JupyterNotebookFile(notebook_folder_path=notebook_folder_path)
            if save_chats_as_notebooks
            else None
        )

        # Instantiates a napari bridge:
        bridge = NapariBridge(viewer=viewer)

        # Register snapshot function:
        if notebook:
            notebook.register_snapshot_function(bridge.take_snapshot)

        # Instantiates server:
        chat_server = NapariChatServer(
            notebook=notebook,
            napari_bridge=bridge,
            main_llm_model_name=main_llm_model_name,
            tool_llm_model_name=tool_llm_model_name,
            temperature=temperature,
            tool_temperature=tool_temperature,
            has_builtin_websearch_tool=has_builtin_websearch_tool,
            memory_type=memory_type,
            agent_personality=agent_personality,
            be_didactic=be_didactic,
            verbose=verbose,
        )

        with asection("Starting chat server..."):

            # Define server thread code:
            def server_thread_function():
                # Start Chat server:
                chat_server.run()

            # Create and start the thread that will run Omega:
            chat_server.server_thread = Thread(
                target=server_thread_function, daemon=True
            )
            chat_server.server_thread.start()

            # Wait for the server to start:
            aprint("Waiting for chat server to start...")
            while not chat_server.running:
                sleep(0.1)

            # Wait a bit more to ensure the server is fully started:
            sleep(0.5)

            aprint("Chat server started.")

            # function to open browser on page:
            def _open_browser():
                url = f"http://127.0.0.1:{chat_server.port}"
                webbrowser.open(url, new=0, autoraise=True)

            # open browser after delay of a few seconds:
            if config.get("open_browser", True):
                QTimer.singleShot(1500, _open_browser)

        # Return the server:
        return chat_server


if __name__ == "__main__":
    # Start chat server:
    start_chat_server()

    # Start qt event event_loop and wait for it to stop:
    napari.run()
