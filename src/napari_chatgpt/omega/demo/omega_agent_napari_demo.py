from queue import Queue
from threading import Thread

import napari
from arbol import aprint

from napari_chatgpt.omega.napari_bridge import NapariBridge
from napari_chatgpt.omega.omega_init import initialize_omega_agent
from napari_chatgpt.utils.openai_key import set_openai_key

# Set OpenAI key:
set_openai_key()

# Instantiates napari viewer:
viewer = napari.Viewer()

# Instantiates a napari bridge:
bridge = NapariBridge(viewer)


def omega_thread(to_napari_queue: Queue,
                 from_napari_queue: Queue):
    agent_chain = initialize_omega_agent(to_napari_queue=to_napari_queue,
                                         from_napari_queue=from_napari_queue,
                                         )
    while True:
        query = input()
        if query == 'quit':
            break
        try:
            result = agent_chain.run(input=query)
            aprint(result)
        except Exception as e:
            return f"Exception: {type(e).__name__} with message: {e.args[0]}"


# Create and start the thread that will run Omega:
omega_thread = Thread(target=omega_thread,
                      args=(bridge.to_napari_queue, bridge.from_napari_queue))
omega_thread.start()

# Start qt event loop and wait for it to stop:
napari.run()
