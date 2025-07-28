"""Main entrypoint for the app."""

import asyncio
import os
import traceback
import webbrowser
from threading import Thread
from time import sleep
from typing import List, Any

import napari
from arbol import aprint, asection, acapture
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from litemind.agent.messages.message import Message
from litemind.agent.tools.base_tool import BaseTool
from litemind.agent.tools.callbacks.base_tool_callbacks import BaseToolCallbacks
from litemind.media.types.media_text import Text
from qtpy.QtCore import QTimer
from starlette.staticfiles import StaticFiles
from uvicorn import Config, Server

from napari_chatgpt.chat_server.chat_response import ChatResponse
from napari_chatgpt.omega_agent.napari_bridge import NapariBridge, _set_viewer_info
from napari_chatgpt.omega_agent.omega_init import initialize_omega_agent
from napari_chatgpt.omega_agent.tools.omega_tool_callbacks import OmegaToolCallbacks
from napari_chatgpt.utils.configuration.app_configuration import AppConfiguration
from napari_chatgpt.utils.network.port_available import find_first_port_available
from napari_chatgpt.utils.notebook.jupyter_notebook import JupyterNotebookFile
from napari_chatgpt.utils.strings.camel_case_to_normal import (
    camel_case_to_lower_case_with_space,
)


class NapariChatServer(BaseToolCallbacks):
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
        fix_imports: bool = True,
        install_missing_packages: bool = True,
        fix_bad_calls: bool = True,
        autofix_mistakes: bool = False,
        autofix_widget: bool = False,
        be_didactic: bool = False,
        verbose: bool = False,
    ):
        """
        Initialize a FastAPI-based WebSocket chat server for real-time interaction with the Omega Agent and napari viewer.
        
        This constructor sets up the chat server, configures agent and tool behavior, manages notebook logging, and prepares the server for asynchronous communication with web clients. The server enables users to interact with the Omega Agent, which can process requests, execute actions in the napari environment, and log chat history and snapshots.
        
        Parameters:
            notebook (JupyterNotebookFile): Notebook file for saving chat history and snapshots.
            napari_bridge (NapariBridge): Bridge for communication with the napari viewer.
            main_llm_model_name (str, optional): Name of the main LLM model for the Omega Agent.
            tool_llm_model_name (str, optional): Name of the LLM model used by tools.
            temperature (float, optional): Sampling temperature for the main LLM model.
            tool_temperature (float, optional): Sampling temperature for the tool LLM model.
            has_builtin_websearch_tool (bool, optional): Whether to enable the built-in web search tool.
            memory_type (str, optional): Type of memory to use for the Omega Agent.
            agent_personality (str, optional): Personality setting for the Omega Agent.
            fix_imports (bool, optional): Whether to automatically fix import statements in executed code.
            install_missing_packages (bool, optional): Whether to install missing packages during code execution.
            fix_bad_calls (bool, optional): Whether to attempt to fix invalid function or method calls.
            autofix_mistakes (bool, optional): Whether to automatically fix mistakes in code execution.
            autofix_widget (bool, optional): Whether to use a widget for autofixing mistakes.
            be_didactic (bool, optional): Whether the agent should provide didactic explanations.
            verbose (bool, optional): Enable verbose logging for debugging and tracing.
        """

        # Flag to keep server running, or stop it:
        self.running = True
        self.uvicorn_server = None

        # Notebook:
        self.notebook: JupyterNotebookFile = notebook

        # Napari bridge:
        self.napari_bridge: NapariBridge = napari_bridge

        # UV event loop:
        self.event_loop = None

        # Instantiate FastAPI:
        self.app = FastAPI()

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

        # Server startup event:
        @self.app.on_event("startup")
        async def startup_event():
            pass

        # Default path:
        @self.app.get("/")
        async def get(request: Request):
            """
            Serves the main chat interface HTML page in response to a GET request.
            
            Parameters:
                request (Request): The incoming HTTP request object.
            
            Returns:
                TemplateResponse: The rendered 'index.html' template for the chat interface.
            """
            return templates.TemplateResponse("index.html", {"request": request})

        # Chat path:
        @self.app.websocket("/chat")
        async def websocket_endpoint(websocket: WebSocket):
            """
            Handles the main WebSocket chat loop, facilitating real-time communication between the user and the Omega Agent.
            
            Upon connection, this endpoint manages the dialog flow: it receives user prompts, processes them through the Omega Agent (which interacts with the napari viewer), and sends responses and status updates back to the user. It also logs chat history and snapshots to the notebook if enabled, and gracefully handles disconnects and errors.
            """
            await websocket.accept()

            # Get the event event_loop:
            self.event_loop = asyncio.get_event_loop()

            # restart a notebook:
            if self.notebook:
                self.notebook.restart()

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
                fix_imports=fix_imports,
                install_missing_packages=install_missing_packages,
                fix_bad_calls=fix_bad_calls,
                autofix_mistakes=autofix_mistakes,
                autofix_widget=autofix_widget,
                be_didactic=be_didactic,
                tool_callbacks=tool_callbacks,
                verbose=verbose,
            )

            dialog_counter = 0

            # Dialog Loop:
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
                        notify_user_omega_thinking(websocket)
                        # result = agent(prompt)
                        result = await self.async_run_in_executor(agent, prompt)
                        notify_user_omega_done_thinking(websocket)

                        with asection(f"Agent response:"):
                            # Extract text from result:
                            for i, message in enumerate(result):
                                with asection(f"Message Block #{i}"):
                                    aprint(message.to_plain_text())

                        send_final_response_to_user(result, websocket)

                        if self.notebook:
                            # Add agent response to notebook:
                            self.notebook.add_markdown_cell(f"### Omega:\n {result}")

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

        async def receive_from_user(websocket: WebSocket) -> str:

            # Receive a question from the user via WebSocket:
            """
            Receives a text message from the user over the WebSocket and sends acknowledgment responses.
            
            Parameters:
                websocket (WebSocket): The active WebSocket connection.
            
            Returns:
                str: The user's input message.
            """
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

        def send_final_response_to_user(result: List[Message], websocket: WebSocket):

            # Filter out non-text messages:
            """
            Send the final agent response to the user over the WebSocket connection.
            
            Filters the agent's response messages to include only text, concatenates them, and sends the result as a final chat message to the user interface.
            """
            text_result = [m for m in result if m.has(Text)]

            # Extract the last message from the result:
            message_str = "\n\n".join([m.to_plain_text() for m in text_result])

            # finalise agent response:
            end_resp = ChatResponse(sender="agent", message=message_str, type="final")

            # Send the response to the user via WebSocket:
            self.sync_handler(websocket.send_json, end_resp.dict())

        def notify_user_omega_thinking(websocket: WebSocket):
            """
            Sends a typing indicator to the user via WebSocket to signal that Omega is processing the request.
            """

            # Format the response as a typing indicator:
            resp = ChatResponse(sender="agent", message="", type="thinking")

            # Send the typing response to the user via WebSocket:
            self.sync_handler(websocket.send_json, resp.dict())

        def notify_user_omega_tool_start(
            websocket: WebSocket, tool: BaseTool, query: str
        ):
            """
            Sends a notification to the user indicating that Omega has started using a specific tool to address their request.
            
            Parameters:
                websocket (WebSocket): The WebSocket connection to the user.
                tool (BaseTool): The tool Omega is using.
                query (str): The user's original request being processed.
            """

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
            """
            Sends a notification to the user about Omega's tool activity, specifically when code is generated and executed.
            
            Parameters:
                websocket (WebSocket): The WebSocket connection to the user.
                tool (BaseTool): The tool being used by Omega.
                activity_type (str): The type of activity performed; must be "coding".
                code (str): The code that was generated and executed.
            
            Raises:
                ValueError: If the activity_type is not "coding".
            """
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
            """
            Sends a notification to the user indicating that Omega has finished using a tool and provides the tool's result.
            
            The result is sent as a message over the WebSocket and optionally logged in the notebook if available.
            """

            # Convert to string if result is not a string:
            message = str(result)

            # Create a ChatResponse object to send to the user:
            resp = ChatResponse(sender="agent", message=message, type="tool_end")

            # Send the message to the user via WebSocket:
            self.sync_handler(websocket.send_json, resp.dict())
            aprint(f"Sent to user via web-ui: {message}")

            # If notebook is available, add the message to it:
            if self.notebook:
                self.notebook.add_markdown_cell("### Omega:\n" + message)

        def notify_user_omega_error(websocket: WebSocket, error: Exception):
            """
            Sends an error notification to the user when Omega's tool encounters an exception.
            
            The error type and message are formatted and sent to the user via WebSocket, and the error is also logged in the notebook if available.
            """

            # Get the type and message of the error:
            error_type = type(error).__name__
            error_message = ", ".join(error.args)

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

        def notify_user_omega_done_thinking(websocket: WebSocket):
            """
            Sends a notification to the user indicating that Omega has finished processing the current request.
            """
            # resp = ChatResponse(sender="agent", message=message, type="finish")
            # await self.websocket.send_json(resp.dict())

    def _start_uvicorn_server(self, app):
        """
        Start the Uvicorn server on the assigned port using the provided FastAPI app.
        
        Parameters:
            app: The FastAPI application instance to serve.
        """
        with asection(f"Starting Uvicorn server on port {self.port}"):
            config = Config(app, port=self.port)
            self.uvicorn_server = Server(config=config)
            self.uvicorn_server.run()

    def run(self):
        """
        Starts the Uvicorn server to run the FastAPI chat application.
        """
        self._start_uvicorn_server(self.app)

    def stop(self):
        """
        Stops the Uvicorn server and marks the chat server as no longer running.
        
        This method signals the Uvicorn server to exit and waits briefly to ensure shutdown.
        """
        with asection("Stopping Uvicorn server"):
            self.running = False
            if self.uvicorn_server:
                self.uvicorn_server.should_exit = True
            sleep(2)
            aprint("Uvicorn server stopped!")

    def sync_handler(self, _callable, *args, **kwargs):
        """
        Schedules a coroutine to run asynchronously in the server's event loop.
        
        Parameters:
            _callable: The coroutine function to execute.
            *args: Positional arguments to pass to the coroutine.
            **kwargs: Keyword arguments to pass to the coroutine.
        """
        self.event_loop.create_task(_callable(*args, **kwargs))

    def async_run_in_executor(self, func, *args):
        """
        Runs a blocking function asynchronously in the event loop's default executor.
        
        Parameters:
            func (callable): The blocking function to execute.
            *args: Arguments to pass to the function.
        
        Returns:
            concurrent.futures.Future: A future representing the execution of the function.
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
    fix_imports: bool = True,
    install_missing_packages: bool = True,
    fix_bad_calls: bool = True,
    autofix_mistakes: bool = False,
    autofix_widget: bool = False,
    be_didactic: bool = False,
    save_chats_as_notebooks: bool = False,
    verbose: bool = False,
):
    """
    Initialize and launch the NapariChatServer, integrating a napari viewer, Omega Agent, and optional notebook logging.
    
    Creates and configures a napari viewer if not provided, sets up notebook logging if enabled, and starts the chat server in a separate thread. Waits for the server to become available, optionally opens the chat interface in a web browser, and returns the running server instance.
    
    Returns:
        NapariChatServer: The running chat server instance.
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
            fix_imports=fix_imports,
            install_missing_packages=install_missing_packages,
            fix_bad_calls=fix_bad_calls,
            autofix_mistakes=autofix_mistakes,
            autofix_widget=autofix_widget,
            be_didactic=be_didactic,
            verbose=verbose,
        )

        with asection("Starting chat server..."):

            # Define server thread code:
            def server_thread_function():
                # Start Chat server:
                chat_server.run()

            # Create and start the thread that will run Omega:
            server_thread = Thread(target=server_thread_function, args=())
            server_thread.start()

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
