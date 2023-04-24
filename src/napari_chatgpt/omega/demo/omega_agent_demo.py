from napari_chatgpt.omega.omega_init import initialize_omega_agent
from napari_chatgpt.utils.openai_key import set_openai_key

set_openai_key()

agent_chain = initialize_omega_agent(to_napari_queue=None,
                                     from_napari_queue=None, )
while True:
    query = input()
    if query == 'quit':
        break
    result = agent_chain.run(input=query)
    print(result)
