import multiprocessing
import os

from langchain.callbacks.manager import AsyncCallbackManager
from langchain.chat_models import ChatOpenAI, ChatAnthropic

from napari_chatgpt.llm.bard import ChatBard
from napari_chatgpt.llm.gpt4all import GPT4AllFixed
from napari_chatgpt.utils.download.gpt4all import get_gpt4all_model


def instantiate_LLMs(llm_model_name: str,
                     temperature: float,
                     chat_callback_handler):
    if 'gpt' in llm_model_name and '4all' not in llm_model_name:
        # Instantiates Main LLM:
        main_llm = ChatOpenAI(
            model_name=llm_model_name,
            verbose=True,
            streaming=True,
            temperature=temperature,
            callback_manager=AsyncCallbackManager(
                [chat_callback_handler])
        )

        # Instantiates Tool LLM:
        tool_llm = ChatOpenAI(
            model_name=llm_model_name,
            verbose=True,
            streaming=True,
            temperature=temperature,
            # callback_manager=AsyncCallbackManager([tool_callback_handler])
        )

        # Instantiates Memory LLM:
        memory_llm = ChatOpenAI(
            model_name=llm_model_name,
            verbose=False,
            temperature=temperature,
            # callback_manager=AsyncCallbackManager([tool_callback_handler])
        )
    if 'bard' in llm_model_name:
        # Instantiates Main LLM:
        main_llm = ChatBard(
            bard_token=os.environ['BARD_KEY'],
            verbose=True,
            streaming=True,
            callback_manager=AsyncCallbackManager(
                [chat_callback_handler])
        )

        # Instantiates Tool LLM:
        tool_llm = ChatBard(
            bard_token=os.environ['BARD_KEY'],
            verbose=True,
            streaming=True,
        )

        # Instantiates Memory LLM:
        memory_llm = ChatBard(
            bard_token=os.environ['BARD_KEY'],
            verbose=False,
        )

    elif 'claude' in llm_model_name:

        # Instantiates Main LLM:
        main_llm = ChatAnthropic(
            model=llm_model_name,
            verbose=True,
            streaming=True,
            temperature=temperature,
            max_tokens_to_sample=4096,
            callback_manager=AsyncCallbackManager(
                [chat_callback_handler])
        )

        # Instantiates Tool LLM:
        tool_llm = ChatAnthropic(
            model=llm_model_name,
            verbose=True,
            streaming=True,
            temperature=temperature,
            max_tokens_to_sample=4096,
            # callback_manager=AsyncCallbackManager([tool_callback_handler])
        )

        # Instantiates Memory LLM:
        memory_llm = ChatAnthropic(
            model=llm_model_name,
            verbose=False,
            temperature=temperature,
            max_tokens_to_sample=4096,
            # callback_manager=AsyncCallbackManager([tool_callback_handler])
        )

    elif 'ggml' in llm_model_name:

        model_path = get_gpt4all_model(llm_model_name)

        n_threads = multiprocessing.cpu_count() - 1

        n_ctx = 1400

        n_predict = 1200

        # Instantiates Main LLM:
        main_llm = GPT4AllFixed(
            model=model_path,
            verbose=True,
            streaming=True,
            n_ctx=n_ctx,
            n_threads=n_threads,
            n_predict=n_predict,
            f16_kv=True,
            temp=temperature,
            callback_manager=AsyncCallbackManager(
                [chat_callback_handler])
        )

        # Too costly to instantiate 3!
        memory_llm = main_llm
        tool_llm = main_llm

    return main_llm, memory_llm, tool_llm
