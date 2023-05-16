"""Main entrypoint for the app."""
import os
import traceback
import webbrowser
from threading import Thread

import napari
from PyQt5.QtCore import QTimer
from arbol import aprint
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from napari_chatgpt.chat_server.callback_handle_chat import ChatCallbackHandler
from napari_chatgpt.chat_server.callback_handler_tool import ToolCallbackHandler
from napari_chatgpt.chat_server.chat_response import ChatResponse
from napari_chatgpt.llm.llms import instantiate_LLMs
from napari_chatgpt.omega.napari_bridge import NapariBridge
from napari_chatgpt.omega.omega_init import initialize_omega_agent
from napari_chatgpt.utils.api_keys.api_key import set_api_key
from napari_chatgpt.utils.download.gpt4all import get_gpt4all_model
from napari_chatgpt.utils.python.installed_packages import is_package_installed


class NapariChatServer:
    def __init__(self,
                 napari_bridge: NapariBridge,
                 llm_model_name: str = 'gpt-3.5-turbo',
                 temperature: float = 0.01,
                 memory_type: str = 'standard',
                 agent_personality: str = 'neutral',
                 ):

        # Napari bridge:
        self.napari_bridge = napari_bridge

        # Instantiate FastAPI:
        self.app = FastAPI()

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

            # Chat callback handler:
            chat_callback_handler = ChatCallbackHandler(websocket)

            # Tool callback handler:
            tool_callback_handler = ToolCallbackHandler(websocket)

            main_llm, memory_llm, tool_llm = instantiate_LLMs(
                llm_model_name=llm_model_name,
                temperature=temperature,
                chat_callback_handler=chat_callback_handler)

            # Agent
            agent_chain = initialize_omega_agent(
                to_napari_queue=napari_bridge.to_napari_queue,
                from_napari_queue=napari_bridge.from_napari_queue,
                main_llm=main_llm,
                tool_llm=tool_llm,
                memory_llm=memory_llm,
                is_async=True,
                chat_callback_handler=chat_callback_handler,
                tool_callback_handler=tool_callback_handler,
                has_human_input_tool=False,
                memory_type=memory_type,
                agent_personality=agent_personality,
            )

            # Dialog Loop:
            while True:
                try:
                    # Receive and send back the client message
                    question = await websocket.receive_text()
                    resp = ChatResponse(sender="user",
                                        message=question)
                    await websocket.send_json(resp.dict())

                    aprint(f"Question: {question}")

                    # Initiates a response -- empty for now:
                    start_resp = ChatResponse(sender="agent",
                                              type="start")
                    await websocket.send_json(start_resp.dict())

                    # call LLM:
                    result = await agent_chain.acall(inputs=question)

                    aprint(f"result={result}")

                    # finalise agent response:
                    end_resp = ChatResponse(sender="agent",
                                            message=result['output'],
                                            type="final")
                    await websocket.send_json(end_resp.dict())

                except WebSocketDisconnect:
                    aprint("websocket disconnect")
                    break

                except Exception as e:
                    traceback.print_exc()
                    resp = ChatResponse(
                        sender="agent",
                        message=f"Sorry, something went wrong ({type(e).__name__}: {e.args[0]}). Try again.",
                        type="error",
                    )
                    await websocket.send_json(resp.dict())

    def run(self):
        import uvicorn
        uvicorn.run(self.app, host="127.0.0.1", port=9000)


def start_chat_server(viewer: napari.Viewer = None,
                      llm_model_name: str = 'gpt-3.5-turbo',
                      temperature: float = 0.01,
                      memory_type: str = 'standard',
                      agent_personality: str = 'neutral'):
    # Set OpenAI key if necessary:
    if 'gpt' in llm_model_name and '4all' not in llm_model_name and is_package_installed(
            'openai'):
        set_api_key('OpenAI')

    if 'bard' in llm_model_name:
        set_api_key('GoogleBard')

    # Set Anthropic key if necessary:
    if 'claude' in llm_model_name and is_package_installed('anthropic'):
        set_api_key('Anthropic')

    # Download GPT4All model if necessary:
    if 'ggml' in llm_model_name and is_package_installed('pygpt4all'):
        # The first this is run it will download the file, afterwards
        # it uses the downloaded file in ~/.gpt4all
        get_gpt4all_model(llm_model_name)

    # Instantiates napari viewer:
    if not viewer:
        viewer = napari.Viewer()

    # Instantiates a napari bridge:
    bridge = NapariBridge(viewer)

    # Instantiates server:
    chat_server = NapariChatServer(bridge,
                                   llm_model_name=llm_model_name,
                                   temperature=temperature,
                                   memory_type=memory_type,
                                   agent_personality=agent_personality)

    # Define server thread code:
    def server_thread_function():
        # Start Chat server:
        chat_server.run()

    # Create and start the thread that will run Omega:s
    server_thread = Thread(target=server_thread_function, args=())
    server_thread.start()

    # function to open browser on page:
    def _open_browser():
        url = "http://127.0.0.1:9000"
        webbrowser.open(url, new=0, autoraise=True)

    # open browser after delay of a few seconds:
    QTimer.singleShot(2000, _open_browser)


if __name__ == "__main__":
    start_chat_server()

    # Start qt event loop and wait for it to stop:
    napari.run()
