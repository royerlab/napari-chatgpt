from pprint import pprint

from napari_chatgpt.utils.ollama.ollama import start_ollama, stop_ollama, \
    is_ollama_running, get_ollama_models


def test_ollama():

    start_ollama()

    if is_ollama_running():

        models = get_ollama_models()
        pprint(models)

        assert len(models) > 0

        selected_model = models[0]

        from langchain.llms import Ollama
        from langchain.callbacks.manager import CallbackManager
        from langchain.callbacks.streaming_stdout import \
            StreamingStdOutCallbackHandler
        llm = Ollama(base_url="http://localhost:11434",
                     model=selected_model,
                     callback_manager=CallbackManager(
                         [StreamingStdOutCallbackHandler()]))

        result = llm("Tell me about the history of AI")

    assert 'artificial intelligence' in result.lower()

    stop_ollama()


