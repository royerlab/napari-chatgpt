import pytest
from arbol import aprint
from duckduckgo_search.exceptions import DuckDuckGoSearchException

from napari_chatgpt.llm.litemind_api import is_llm_available
from napari_chatgpt.utils.web.duckduckgo import summary_ddg


@pytest.mark.skipif(not is_llm_available(), reason="requires LLM to run")
def test_duckduckgo_search_overview_summary():
    try:
        query = "Mickey Mouse"
        text = summary_ddg(query, do_summarize=True)
        aprint(text)
        # Skip test if rate limited or no results (flaky external dependency)
        if "Web search failed" in text or text == "No results.":
            pytest.skip("DuckDuckGo search rate limited or unavailable")
        assert "Mickey" in text

    except DuckDuckGoSearchException as e:
        pytest.skip(f"DuckDuckGo search unavailable: {e}")


def test_duckduckgo_search_overview():
    try:
        query = "Mickey Mouse"
        text = summary_ddg(query, do_summarize=False)
        aprint(text)
        # Skip test if rate limited or no results (flaky external dependency)
        if "Web search failed" in text or text == "No results.":
            pytest.skip("DuckDuckGo search rate limited or unavailable")
        assert "Mickey" in text

    except DuckDuckGoSearchException as e:
        pytest.skip(f"DuckDuckGo search unavailable: {e}")
