"""Demo script that launches the Omega chat server with a napari viewer.

Run this module directly to start a napari viewer alongside the WebSocket
chat server, then open the web UI in a browser to interact with Omega.
"""

import napari as napari

from napari_chatgpt.chat_server.chat_server import start_chat_server

if __name__ == "__main__":
    start_chat_server()

    napari.run()
