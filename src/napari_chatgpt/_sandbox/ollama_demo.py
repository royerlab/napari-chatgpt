# start Ollama server:
from pprint import pprint

from napari_chatgpt.llm.ollama import OllamaFixed
from napari_chatgpt.utils.ollama.ollama import start_ollama, get_ollama_models

model_list = get_ollama_models()

pprint(model_list)

#model = model_list[-1]
model = 'mixtral:latest'

start_ollama()

# Instantiates Main LLM:
main_llm = OllamaFixed(
    base_url="http://localhost:11434",
    model=model,
    verbose=True,
    temperature=0)

# interactive loop:
while True:
    # get input:
    input_text = input("Enter input: ")

    # run main_llm:
    result = main_llm(input_text)

    # Display result:
    pprint(result)