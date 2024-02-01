"""Main entrypoint for the app."""
import os
import traceback
import webbrowser
from threading import Thread
from time import sleep

import napari
from PyQt5.QtCore import QTimer
from arbol import aprint, asection
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from langchain.memory import ConversationTokenBufferMemory, \
    ConversationBufferMemory
from langchain.schema import get_buffer_string, BaseMemory
from starlette.staticfiles import StaticFiles
from uvicorn import Config, Server

from napari_chatgpt.chat_server.callbacks.callbacks_arbol_stdout import \
    ArbolCallbackHandler
from napari_chatgpt.chat_server.callbacks.callbacks_handle_chat import \
    ChatCallbackHandler
from napari_chatgpt.chat_server.callbacks.callbacks_handler_tool import \
    ToolCallbackHandler
from napari_chatgpt.chat_server.chat_response import ChatResponse
from napari_chatgpt.llm.llms import instantiate_LLMs
from napari_chatgpt.omega.memory.memory import OmegaMemory
from napari_chatgpt.omega.napari_bridge import NapariBridge, _set_viewer_info

from napari_chatgpt.omega.omega_init import initialize_omega_agent
from napari_chatgpt.utils.api_keys.api_key import set_api_key
from napari_chatgpt.utils.configuration.app_configuration import \
    AppConfiguration
from napari_chatgpt.utils.notebook.jupyter_notebook import JupyterNotebookFile
from napari_chatgpt.utils.openai.default_model import \
    get_default_openai_model_name
from napari_chatgpt.utils.python.installed_packages import is_package_installed


class NapariChatServer:
    def __init__(self,
                 notebook: JupyterNotebookFile,
                 napari_bridge: NapariBridge,
                 main_llm_model_name: str = get_default_openai_model_name(),
                 tool_llm_model_name: str = None,
                 temperature: float = 0.01,
                 tool_temperature: float = 0.01,
                 memory_type: str = 'standard',
                 agent_personality: str = 'neutral',
                 fix_imports: bool = True,
                 install_missing_packages: bool = True,
                 fix_bad_calls: bool = True,
                 autofix_mistakes: bool = False,
                 autofix_widget: bool = False,
                 be_didactic: bool = False,
                 verbose: bool = False
                 ):

        # Flag to keep server running, or stop it:
        self.running = True
        self.uvicorn_server = None

        # Notebook:
        self.notebook: JupyterNotebookFile = notebook

        # Napari bridge:
        self.napari_bridge: NapariBridge = napari_bridge

        # Instantiate FastAPI:
        self.app = FastAPI()

        # get configuration
        config = AppConfiguration('omega')

        # port:
        self.port = config.get('port', 9000)

        # Mount static files:
        static_files_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'static')
        self.app.mount("/static", StaticFiles(directory=static_files_path),
                       name="static")

        templates_files_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'templates')
        # Load Jinja2 templates:
        templates = Jinja2Templates(directory=templates_files_path)

        # Server startup event:
        @self.app.on_event("startup")
        async def startup_event():
            pass

        # Default path:
        @self.app.get("/")
        async def get(request: Request):
            return templates.TemplateResponse("index.html",
                                              {"request": request})

        # Chat path:
        @self.app.websocket("/chat")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()

            # restart a notebook:
            if self.notebook:
                self.notebook.restart()

            # Chat callback handler:
            chat_callback_handler = ChatCallbackHandler(websocket=websocket,
                                                        notebook=self.notebook,
                                                        verbose=verbose)

            # Tool callback handler:
            tool_callback_handler = ToolCallbackHandler(websocket=websocket,
                                                        notebook=self.notebook,
                                                        verbose=verbose)

            # Memory callback handler:
            memory_callback_handler = ArbolCallbackHandler('Memory')

            main_llm, memory_llm, tool_llm, max_token_limit = instantiate_LLMs(
                main_llm_model_name=main_llm_model_name,
                tool_llm_model_name=tool_llm_model_name,
                temperature=temperature,
                tool_temperature=tool_temperature,
                chat_callback_handler=chat_callback_handler,
                tool_callback_handler=tool_callback_handler,
                memory_callback_handler=memory_callback_handler
            )

            # Instantiate Memory:
            memory: BaseMemory = None
            if memory_type == 'bounded':
                memory = ConversationTokenBufferMemory(
                    memory_key="chat_history",
                    return_messages=True,
                    max_token_limit=max_token_limit)
            elif memory_type == 'infinite':
                memory = ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True)
            elif memory_type == 'hybrid':
                memory = OmegaMemory(
                    llm=memory_llm,
                    memory_key="chat_history",
                    return_messages=True,
                    max_token_limit=max_token_limit)
            else:
                raise ValueError('Invalid Memory parameter!')

            # Agent
            agent_chain = initialize_omega_agent(
                to_napari_queue=napari_bridge.to_napari_queue,
                from_napari_queue=napari_bridge.from_napari_queue,
                main_llm_model_name=main_llm_model_name,
                main_llm=main_llm,
                tool_llm=tool_llm,
                is_async=True,
                chat_callback_handler=chat_callback_handler,
                tool_callback_handler=tool_callback_handler,
                notebook=self.notebook,
                has_human_input_tool=False,
                memory=memory,
                agent_personality=agent_personality,
                fix_imports=fix_imports,
                install_missing_packages=install_missing_packages,
                fix_bad_calls=fix_bad_calls,
                autofix_mistakes=autofix_mistakes,
                autofix_widget=autofix_widget,
                be_didactic=be_didactic,
                verbose=verbose
            )

            dialog_counter = 0

            # Dialog Loop:
            while True:
                with asection(f"Dialog iteration {dialog_counter}:"):
                    try:
                        # Receive and send back the client message
                        question = await websocket.receive_text()
                        resp = ChatResponse(sender="user",
                                            message=question)
                        await websocket.send_json(resp.dict())
                        if self.notebook:
                            self.notebook.add_markdown_cell("### User:\n" + question)

                        aprint(f"Human Question/Request:\n{question}\n\n")

                        # Initiates a response -- empty for now:
                        start_resp = ChatResponse(sender="agent",
                                                  type="start")
                        await websocket.send_json(start_resp.dict())

                        # get napari viewer info::
                        viewer_info = self.napari_bridge.get_viewer_info()
                        _set_viewer_info(viewer_info)

                        # call LLM:
                        result = await agent_chain.acall(question)

                        aprint(
                            f"Agent response:\n{result['chat_history'][-1]}\n\n")

                        # finalise agent response:
                        end_resp = ChatResponse(sender="agent",
                                                message=result['output'],
                                                type="final")
                        await websocket.send_json(end_resp.dict())

                        if self.notebook:
                            # Add agent response to notebook:
                            self.notebook.add_markdown_cell("### Omega:\n" + result['output'])

                            # Add snapshot to notebook:
                            self.notebook.take_snapshot()

                            # write notebook:
                            self.notebook.write()

                        # Current chat history:
                        current_chat_history = get_buffer_string(
                            result['chat_history'])

                        with asection(
                                f"Current chat history of {len(result['chat_history'])} messages:"):
                            aprint(current_chat_history)


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

    def _start_uvicorn_server(self, app):
        config = Config(app, port=self.port)
        self.uvicorn_server = Server(config=config)
        self.uvicorn_server.run()

    def run(self):
        self._start_uvicorn_server(self.app)

    def stop(self):
        self.running = False
        if self.uvicorn_server:
            self.uvicorn_server.should_exit = True
        sleep(2)


def start_chat_server(viewer: napari.Viewer = None,
                      main_llm_model_name: str = get_default_openai_model_name(),
                      tool_llm_model_name: str = None,
                      temperature: float = 0.01,
                      tool_temperature: float = 0.01,
                      memory_type: str = 'standard',
                      agent_personality: str = 'neutral',
                      fix_imports: bool = True,
                      install_missing_packages: bool = True,
                      fix_bad_calls: bool = True,
                      autofix_mistakes: bool = False,
                      autofix_widget: bool = False,
                      be_didactic: bool = False,
                      save_chats_as_notebooks: bool = False,
                      verbose: bool = False
                      ):

    # get configuration:
    config = AppConfiguration('omega')

    # Set OpenAI key if necessary:
    if ('gpt' in main_llm_model_name or 'gpt' in tool_llm_model_name )and is_package_installed(
            'openai'):
        set_api_key('OpenAI')

    # Set Anthropic key if necessary:
    if ('claude' in main_llm_model_name or 'claude' in tool_llm_model_name) and is_package_installed('anthropic'):
        set_api_key('Anthropic')

    # Instantiates napari viewer:
    if not viewer:
        viewer = napari.Viewer()

    # Instantiates a notebook:
    notebook = JupyterNotebookFile(notebook_folder_path=config.get('notebook_path')) if save_chats_as_notebooks else None

    # Instantiates a napari bridge:
    bridge = NapariBridge(viewer=viewer)

    # Register snapshot function:
    notebook.register_snapshot_function(bridge.take_snapshot)

    # Instantiates server:
    chat_server = NapariChatServer(notebook=notebook,
                                   napari_bridge=bridge,
                                   main_llm_model_name=main_llm_model_name,
                                   tool_llm_model_name=tool_llm_model_name,
                                   temperature=temperature,
                                   tool_temperature=tool_temperature,
                                   memory_type=memory_type,
                                   agent_personality=agent_personality,
                                   fix_imports=fix_imports,
                                   install_missing_packages=install_missing_packages,
                                   fix_bad_calls=fix_bad_calls,
                                   autofix_mistakes=autofix_mistakes,
                                   autofix_widget=autofix_widget,
                                   be_didactic=be_didactic,
                                   verbose=verbose
                                   )

    # Define server thread code:
    def server_thread_function():
        # Start Chat server:
        chat_server.run()

    # Create and start the thread that will run Omega:
    server_thread = Thread(target=server_thread_function, args=())
    server_thread.start()

    # function to open browser on page:
    def _open_browser():
        url = f"http://127.0.0.1:{chat_server.port}"
        webbrowser.open(url, new=0, autoraise=True)

    # open browser after delay of a few seconds:
    if config.get('open_browser', True):
        QTimer.singleShot(2000, _open_browser)

    # Return the server:
    return chat_server


if __name__ == "__main__":

    # Start chat server:
    start_chat_server()

    # Start qt event loop and wait for it to stop:
    napari.run()
