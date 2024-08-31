import pytest
from arbol import aprint
from duckduckgo_search.exceptions import RatelimitException

from napari_chatgpt.utils.api_keys.api_key import is_api_key_available
from napari_chatgpt.utils.web.wikipedia import search_wikipedia

import os

# Skip tests that require API keys in Github Actions
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions.")
def test_wikipedia_search_MM():

    try:
        term = 'Mickey Mouse'

        # Get summary of wikipedia article:
        text = search_wikipedia(term,
                                do_summarize=False)

        aprint(text)

        assert 'Mickey Mouse' in text

    except RatelimitException as e:
        aprint(f"RatelimitException: {e}")
        import traceback
        traceback.print_exc()

@pytest.mark.skipif(IN_GITHUB_ACTIONS or not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run and doesn't work in Github Actions.")
def test_wikipedia_search_AE():

    try:
        term = 'Albert Einstein'

        # Get summary of wikipedia article:
        text = search_wikipedia(term,
                                do_summarize=True)

        aprint(text)

        assert 'Albert Einstein' in text

    except RatelimitException as e:
        aprint(f"RatelimitException: {e}")
        import traceback
        traceback.print_exc()




@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_wikipedia_search_CZB():

    try:
        term = 'CZ Biohub'

        # Get summary of wikipedia article:
        text = search_wikipedia(term,
                                do_summarize=True)

        aprint(text)

        assert 'CZ Biohub' in text

    except RatelimitException as e:
        aprint(f"RatelimitException: {e}")









