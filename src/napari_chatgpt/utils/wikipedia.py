# Code vendored from: https://github.com/Nv7-GitHub/googlesearch/blob/master/googlesearch/__init__.py
from langchain.llms import BaseLLM

from napari_chatgpt.utils.google import search_google
from napari_chatgpt.utils.scrapper import text_from_url
from napari_chatgpt.utils.summarizer import summarize


def search_wikipedia(query: str,
                     lang: str = "english",
                     max_text_length: int = 4000,
                     summarise_page: bool = False,
                     llm: BaseLLM = None) -> str:
    # Run a google search specifically on wikipedia:
    urls = search_google(query=f"{query} site:wikipedia.org",
                         num_results=10,
                         lang='en')

    # convert generator to list:
    urls = list(urls)

    # pick the first url:
    url = urls[0]

    # Get text from first url:
    text = text_from_url(url=url)

    # Limit text length:
    text = text[:max_text_length]

    if summarise_page:
        text = summarize(text, llm=llm)

    return text
