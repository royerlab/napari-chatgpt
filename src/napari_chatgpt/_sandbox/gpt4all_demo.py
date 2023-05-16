import multiprocessing

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from napari_chatgpt.llm.gpt4all import GPT4AllFixed
from napari_chatgpt.utils.download.gpt4all import get_gpt4all_model

llm_model_name = 'ggml-gpt4all-l13b-snoozy'

model_path = get_gpt4all_model(llm_model_name)

n_threads = multiprocessing.cpu_count() - 1

n_ctx = 1024

n_predict = 2048

temperature = 0.1

# Instantiates Main LLM:
model = GPT4AllFixed(
    model=model_path,
    verbose=True,
    streaming=True,
    n_ctx=n_ctx,
    n_threads=n_threads,
    n_predict=n_predict,
    f16_kv=False,
    temp=temperature
)

callbacks = [StreamingStdOutCallbackHandler()]

# Generate text. Tokens are streamed through the callback manager.
result = model("Who are you?\n ", callbacks=callbacks)
