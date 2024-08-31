import pytest
from arbol import aprint
from duckduckgo_search.exceptions import RatelimitException

from napari_chatgpt.utils.api_keys.api_key import is_api_key_available
from napari_chatgpt.utils.web.duckduckgo import summary_ddg


@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_duckduckgo_search_overview_summary():

    try:
        query = 'Mickey Mouse'
        text = summary_ddg(query, do_summarize=True)
        aprint(text)
        assert 'Mickey' in text
        assert 'Web search failed' not in text

    except RatelimitException as e:
        aprint(f"RatelimitException: {e}")
        import traceback
        traceback.print_exc()




def test_duckduckgo_search_overview():

    try:
        query = 'Mickey Mouse'
        text = summary_ddg(query, do_summarize=False)
        aprint(text)
        assert 'Mickey' in text
        assert 'Web search failed' not in text

    except RatelimitException as e:
        aprint(f"RatelimitException: {e}")
        import traceback
        traceback.print_exc()
