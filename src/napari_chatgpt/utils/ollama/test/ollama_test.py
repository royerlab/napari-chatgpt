from pprint import pprint

import pytest

from napari_chatgpt.utils.ollama.ollama import OllamaFixed
from napari_chatgpt.utils.ollama.ollama_server import start_ollama, stop_ollama, \
    is_ollama_running, get_ollama_models


@pytest.mark.skipif(not is_ollama_running(),
                    reason="requires an ollama instance to run")
def test_ollama():

    start_ollama()

    if is_ollama_running():

        models = get_ollama_models()
        pprint(models)

        assert len(models) > 0

        selected_model = models[0]

        from langchain.callbacks.streaming_stdout import \
            StreamingStdOutCallbackHandler
        llm = OllamaFixed(base_url="http://localhost:11434",
                     model=selected_model,
                     callbacks=[StreamingStdOutCallbackHandler()])

        result = llm.invoke("Tell me about the history of AI")

        pprint(result)

    assert 'artificial intelligence' in result.lower()

    stop_ollama()


