import pytest
from arbol import aprint
from ddgs.exceptions import RatelimitException

from napari_chatgpt.llm.litemind_api import is_llm_available
from napari_chatgpt.utils.web.duckduckgo import summary_ddg


@pytest.mark.skipif(not is_llm_available(), reason="requires LLM to run")
def test_duckduckgo_search_overview_summary():
    try:
        query = "Mickey Mouse"
        text = summary_ddg(query, do_summarize=True)
        aprint(text)
        assert "Mickey" in text
        assert "Web search failed" not in text

    except RatelimitException as e:
        aprint(f"RatelimitException: {e}")
        import traceback

        traceback.print_exc()


def test_duckduckgo_search_overview():
    try:
        query = "Mickey Mouse"
        text = summary_ddg(query, do_summarize=False)
        aprint(text)
        assert "Mickey" in text
        assert "Web search failed" not in text

    except RatelimitException as e:
        aprint(f"RatelimitException: {e}")
        import traceback

        traceback.print_exc()
