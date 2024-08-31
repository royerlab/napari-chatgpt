import pytest
from arbol import aprint
from duckduckgo_search.exceptions import RatelimitException

from napari_chatgpt.utils.api_keys.api_key import is_api_key_available
from napari_chatgpt.utils.web.metasearch import metasearch


@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_metasearch_summary():

    try:
        query = 'Mickey Mouse'
        text = metasearch(query, do_summarize=True)
        aprint(text)
        assert 'Mickey' in text
        #assert 'Web search failed' not in text

    except RatelimitException as e:
        aprint(f"RatelimitException: {e}")
        import traceback
        traceback.print_exc()


def test_metasearch():

    try:
        query = 'Mickey Mouse'
        text = metasearch(query, do_summarize=False)
        aprint(text)
        assert 'Mickey' in text
        #assert 'Web search failed' not in text

    except RatelimitException as e:
        aprint(f"RatelimitException: {e}")
        import traceback
        traceback.print_exc()




