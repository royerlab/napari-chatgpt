import pytest
from duckduckgo_search.exceptions import DuckDuckGoSearchException

from napari_chatgpt.llm.litemind_api import is_llm_available
from napari_chatgpt.utils.web.metasearch import metasearch


@pytest.mark.integration
@pytest.mark.skipif(not is_llm_available(), reason="requires LLM to run")
def test_metasearch_summary():
    try:
        query = "Mickey Mouse"
        text = metasearch(query, do_summarize=True)
        if "No results" in text and "Mickey" not in text:
            pytest.skip("Metasearch returned no results")
        assert "Mickey" in text

    except DuckDuckGoSearchException as e:
        pytest.skip(f"DuckDuckGo search unavailable: {e}")


@pytest.mark.integration
def test_metasearch():
    try:
        query = "Mickey Mouse"
        text = metasearch(query, do_summarize=False)
        if "No results" in text and "Mickey" not in text:
            pytest.skip("Metasearch returned no results")
        assert "Mickey" in text

    except DuckDuckGoSearchException as e:
        pytest.skip(f"DuckDuckGo search unavailable: {e}")
