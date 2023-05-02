import pytest
from arbol import aprint

from napari_chatgpt.utils.openai_key import is_openai_key_available
from src.napari_chatgpt.utils.wikipedia import search_wikipedia

def test_wikipedia_search_MM():
    term = 'Mickey Mouse'

    # Get summary of wikipedia article:
    text = search_wikipedia(term,
                            do_summarize=False)

    aprint(text)

@pytest.mark.skipif(not is_openai_key_available(), reason="requires OpenAI key to run")
def test_wikipedia_search_AE():
    term = 'Albert Einstein'

    # Get summary of wikipedia article:
    text = search_wikipedia(term,
                            do_summarize=True)

    aprint(text)

@pytest.mark.skipif(not is_openai_key_available(), reason="requires OpenAI key to run")
def test_wikipedia_search_CZB():
    term = 'CZ Biohub'

    # Get summary of wikipedia article:
    text = search_wikipedia(term,
                            do_summarize=True)

    aprint(text)


