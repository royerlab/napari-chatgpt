"""Main entrypoint for the app."""
import logging
import os

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import AsyncCallbackManager
from langchain.memory import ChatMessageHistory
from langchain.schema import get_buffer_string
from napari import Viewer
from starlette.staticfiles import StaticFiles

from chat_response import ChatResponse
from napari_chatgpt.openai_key import set_openai_key
from src.napari_chatgpt.chat_server.callbacks import StreamingLLMCallbackHandler
from src.napari_chatgpt.utils.installed_packages import installed_package_list
from src.napari_chatgpt.chat_server.prompt_templates import default_template


class NapariChatServer:
    def __init__(self, viewer: Viewer):

        # Package list:
        package_list = installed_package_list()

        # Instantiate FastAPI:
        self.app = FastAPI()

        # Mount static files:
        package_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'static')
        self.app.mount("/static", StaticFiles(directory=package_path),
                       name="static")

        # Load Jinja2 templates:
        templates = Jinja2Templates(directory="templates")

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

            # Stream handler:
            stream_handler = StreamingLLMCallbackHandler(websocket)

            # Stream manager:
            stream_manager = AsyncCallbackManager([stream_handler])

            # Instantiates OpenAI's LLM:
            streaming_llm = ChatOpenAI(
                model_name='gpt-3.5-turbo',
                streaming=True,
                callback_manager=stream_manager,
                verbose=True,
                temperature=0.02,
            )

            # Chat history:
            chat_history = ChatMessageHistory()

            # Chain:
            conversation = LLMChain(
                prompt=self.get_prompt_template(),
                llm=streaming_llm,
                #callback_manager=callback_manager,
                verbose=True
            )

            # Dialog Loop:
            while True:
                try:
                    # Receive and send back the client message
                    question = await websocket.receive_text()
                    resp = ChatResponse(sender="you",
                                        message=question,
                                        type="stream")
                    await websocket.send_json(resp.dict())

                    # Append to chat history user message:
                    chat_history.add_user_message(question)

                    print(f"Question: {question}")

                    # Initiates a response -- empty for now:
                    start_resp = ChatResponse(sender="bot",
                                              message="",
                                              type="start")
                    await websocket.send_json(start_resp.dict())

                    # Variabels for prompt:
                    variables = {"input": question,
                                 "packages": ', '.join(package_list),
                                 "history": get_buffer_string(chat_history.messages,
                                                              human_prefix="User (human)",
                                                              ai_prefix="Omega (AI)"),
                         }

                    # call LLM:
                    result = await conversation.acall(variables)

                    # printout prompt:
                    prompt_str = self.get_prompt_template().format(**variables)
                    print(f"Prompt: {prompt_str}")

                    # Append to chat history:
                    chat_history.add_ai_message(result["text"])

                    # finalise bot response:
                    end_resp = ChatResponse(sender="bot", message="",
                                            type="end")
                    await websocket.send_json(end_resp.dict())

                except WebSocketDisconnect:
                    logging.info("websocket disconnect")
                    break

                except Exception as e:
                    logging.error(e)
                    resp = ChatResponse(
                        sender="bot",
                        message="Sorry, something went wrong. Try again.",
                        type="error",
                    )
                    await websocket.send_json(resp.dict())

    def get_prompt_template(self):
        prompt_template = PromptTemplate(template=default_template,
                                         input_variables=["input", "history", "packages"])

        return prompt_template

    def run(self):
        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=9000)


if __name__ == "__main__":

    # Set OpenAI key:
    set_openai_key()

    chat_server = NapariChatServer(None)
    chat_server.run()
