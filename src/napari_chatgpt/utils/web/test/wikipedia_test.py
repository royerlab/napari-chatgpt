import pytest
from arbol import aprint

from napari_chatgpt.utils.api_keys.api_key import is_api_key_available
from napari_chatgpt.utils.web.wikipedia import search_wikipedia


def test_wikipedia_search_MM():
    term = 'Mickey Mouse'

    # Get summary of wikipedia article:
    text = search_wikipedia(term,
                            do_summarize=False)

    aprint(text)


@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_wikipedia_search_AE():
    term = 'Albert Einstein'

    # Get summary of wikipedia article:
    text = search_wikipedia(term,
                            do_summarize=True)

    aprint(text)


@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_wikipedia_search_CZB():
    term = 'CZ Biohub'

    # Get summary of wikipedia article:
    text = search_wikipedia(term,
                            do_summarize=True)

    aprint(text)
