import pytest
from arbol import aprint
from duckduckgo_search.exceptions import RatelimitException

from napari_chatgpt.utils.api_keys.api_key import is_api_key_available
from napari_chatgpt.utils.web.wikipedia import search_wikipedia


def test_wikipedia_search_MM():

    try:
        term = 'Mickey Mouse'

        # Get summary of wikipedia article:
        text = search_wikipedia(term,
                                do_summarize=False)

        aprint(text)

    except RatelimitException as e:
        aprint(f"RatelimitException: {e}")
        aprint(f"RatelimitException: {e.response}")
        aprint(f"RatelimitException: {e.response.text}")



@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_wikipedia_search_AE():

    try:
        term = 'Albert Einstein'

        # Get summary of wikipedia article:
        text = search_wikipedia(term,
                                do_summarize=True)

        aprint(text)
    except RatelimitException as e:
        aprint(f"RatelimitException: {e}")
        aprint(f"RatelimitException: {e.response}")
        aprint(f"RatelimitException: {e.response.text}")


@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_wikipedia_search_CZB():

    try:
        term = 'CZ Biohub'

        # Get summary of wikipedia article:
        text = search_wikipedia(term,
                                do_summarize=True)

        aprint(text)

    except RatelimitException as e:
        aprint(f"RatelimitException: {e}")
        aprint(f"RatelimitException: {e.response}")
        aprint(f"RatelimitException: {e.response.text}")



