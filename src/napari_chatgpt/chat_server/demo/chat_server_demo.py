import napari as napari

from napari_chatgpt.chat_server.chat_server import start_chat_server

if __name__ == "__main__":
    start_chat_server()

    napari.run()
