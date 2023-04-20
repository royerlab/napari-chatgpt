import os

from gptcache import Cache, get_data_manager
from gptcache import cache
from gptcache.adapter.langchain_models import LangChainLLMs
from gptcache.processor.pre import get_prompt
from langchain.llms.base import LLM

from napari_chatgpt.utils.folders import get_or_create_folder_in_home


def wrap_llm(llm: LLM,
             cache_name: str = 'cache_data',
             max_cache_size: int = 512):

    # TODO: not functional!

    # get or create llm cache folder:
    cache_folder = get_or_create_folder_in_home('.llmcache')

    # cache file path:
    cache_file = os.path.join(cache_folder, cache_name)

    # Does file exist?
    cache_file_exists = os.path.isfile(cache_file)

    # Instantiates cache:
    llm_cache = Cache()

    # Instantiates data manager:
    data_manager = get_data_manager(data_path=cache_file, max_size=max_cache_size)

    # Initialises cache:
    cache.init(data_manager=data_manager,
               pre_embedding_func=get_prompt,
               )

    # Set key:
    cache.set_openai_key()

    # Wrap LLM:
    llm = LangChainLLMs(llm=llm,
                        llm_cache=llm_cache)

    return llm