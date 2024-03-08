from time import sleep

from arbol import aprint

from napari_chatgpt.utils.configuration.app_configuration import \
    AppConfiguration
from napari_chatgpt.utils.ollama.ollama_server import is_ollama_running
from napari_chatgpt.utils.openai.max_token_limit import openai_max_token_limit


def instantiate_LLMs(main_llm_model_name: str,
                     tool_llm_model_name: str,
                     temperature: float,
                     tool_temperature: float,
                     chat_callback_handler,
                     tool_callback_handler,
                     memory_callback_handler,
                     verbose: bool = False
                     ):

    # If the tool LLM model name is not specified, then we use the same as for the main LLM:
    if not tool_llm_model_name:
        tool_llm_model_name = main_llm_model_name

    aprint(f"Instantiating LLMs with models: main:'{main_llm_model_name}', tool:{tool_llm_model_name}, t={temperature}, t_tool={tool_temperature}. ")

    # Instantiate all three LLMs needed for the agent:
    main_llm, max_token_limit = _instantiate_single_llm(main_llm_model_name, verbose, temperature, True, chat_callback_handler)
    tool_llm, _ = _instantiate_single_llm(tool_llm_model_name, verbose, tool_temperature, True, tool_callback_handler)
    memory_llm, _ = _instantiate_single_llm(main_llm_model_name, False, temperature, False, memory_callback_handler)

    # Return the three LLMs and the maximum token limit for the main LLM:
    return main_llm, memory_llm, tool_llm, max_token_limit


def _instantiate_single_llm(llm_model_name: str,
                            verbose: bool = False,
                            temperature: float = 0.0,
                            streaming: bool = True,
                            callback_handler=None,):

    # Get app configuration class:
    config = AppConfiguration('omega')

    if 'gpt-' in llm_model_name:

        # Import OpenAI ChatGPT model:
        from langchain_openai import ChatOpenAI

        # Instantiates Main LLM:
        llm = ChatOpenAI(
            model_name=llm_model_name,
            verbose=verbose,
            streaming=streaming,
            temperature=temperature,
            callbacks=[callback_handler]
        )

        max_token_limit = openai_max_token_limit(llm_model_name)

        return llm, max_token_limit

    elif 'claude' in llm_model_name:

        # Import Claude LLM:
        from langchain.chat_models import ChatAnthropic

        max_token_limit = 8000

        # Instantiates Main LLM:
        llm = ChatAnthropic(
            model=llm_model_name,
            verbose=verbose,
            streaming=streaming,
            temperature=temperature,
            max_tokens_to_sample=max_token_limit,
            callbacks=[callback_handler])

        return llm, max_token_limit

    elif 'ollama' in llm_model_name:

        # Import Ollama LLM model:
        from napari_chatgpt.utils.ollama.ollama import OllamaFixed
        from napari_chatgpt.utils.ollama.ollama_server import start_ollama

        # Remove ollama prefix:
        llm_model_name = llm_model_name.removeprefix('ollama_')

        # ollama port:
        ollama_port = config.get('ollama_port', 11434)

        # ollama machine host:
        ollama_host = config.get('ollama_host', 'localhost')

        # start Ollama server if needed:
        if ollama_host not in ['localhost', '127.0.0.1', '0.0.0.0']:
            aprint(f"Ollama server is not running on the same machine as the agent. Please make sure the Ollama server is running on '{ollama_host}' and the port '{ollama_port}' is open. ")
        else:
            # Start Ollama server:
            start_ollama()

            # Wait a bit:
            sleep(3)

        # Make ure that Ollama is running
        if not is_ollama_running(ollama_host, ollama_port):
            aprint(f"Ollama server is not running on '{ollama_host}'. Please start the Ollama server on this machine and make sure the port '{ollama_port}' is open. ")
            raise Exception("Ollama server is not running!")

        # Max token limit:
        max_token_limit = config.get('ollama_max_token_limit', 4096)

        # Instantiates Main LLM:
        llm = OllamaFixed(
            base_url=f"http://{ollama_host}:{ollama_port}",
            model=llm_model_name,
            verbose=verbose,
            #streaming=streaming,
            temperature=temperature,
            callbacks=[callback_handler]
        )

        return llm, max_token_limit



