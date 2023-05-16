import pytest
from arbol import aprint

from napari_chatgpt.utils.api_keys.api_key import is_api_key_available
from napari_chatgpt.utils.web.metasearch import metasearch


@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_metasearch_summary():
    query = 'Mickey Mouse'
    text = metasearch(query, do_summarize=True)
    aprint(text)
    assert 'Mickey' in text


def test_metasearch():
    query = 'Mickey Mouse'
    text = metasearch(query, do_summarize=False)
    aprint(text)
    assert 'Mickey' in text
