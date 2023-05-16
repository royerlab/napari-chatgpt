import pytest
from arbol import aprint

from napari_chatgpt.utils.api_keys.api_key import is_api_key_available
from napari_chatgpt.utils.web.duckduckgo import summary_ddg


@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_duckduckgo_search_overview_summary():
    query = 'Mickey Mouse'
    text = summary_ddg(query, do_summarize=True)
    aprint(text)
    assert 'Mickey' in text


def test_duckduckgo_search_overview():
    query = 'Mickey Mouse'
    text = summary_ddg(query, do_summarize=False)
    aprint(text)
    assert 'Mickey' in text
