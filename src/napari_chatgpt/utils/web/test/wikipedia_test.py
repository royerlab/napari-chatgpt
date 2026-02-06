import os

import pytest
from arbol import aprint
from duckduckgo_search.exceptions import DuckDuckGoSearchException

from napari_chatgpt.llm.litemind_api import is_llm_available
from napari_chatgpt.utils.web.wikipedia import search_wikipedia

# Skip tests that require API keys in Github Actions
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions.")
def test_wikipedia_search_MM():
    try:
        term = "Mickey Mouse"

        # Get summary of wikipedia article:
        text = search_wikipedia(term, do_summarize=False)

        aprint(text)

        # Skip if search returned no results (flaky external dependency)
        if not text or text.strip() == "":
            pytest.skip("Wikipedia/DuckDuckGo search returned no results")

        assert "Mickey Mouse" in text or "Mickey" in text

    except DuckDuckGoSearchException as e:
        pytest.skip(f"DuckDuckGo search unavailable: {e}")


@pytest.mark.skipif(
    IN_GITHUB_ACTIONS or not is_llm_available(),
    reason="requires LLM to run and doesn't work in Github Actions.",
)
def test_wikipedia_search_AE():
    try:
        term = "Albert Einstein"

        # Get summary of wikipedia article:
        text = search_wikipedia(term, do_summarize=True)

        aprint(text)

        # Skip if search returned no results (flaky external dependency)
        if not text or text.strip() == "":
            pytest.skip("Wikipedia/DuckDuckGo search returned no results")

        assert "Albert Einstein" in text or "Einstein" in text

    except DuckDuckGoSearchException as e:
        pytest.skip(f"DuckDuckGo search unavailable: {e}")


@pytest.mark.skipif(
    IN_GITHUB_ACTIONS or not is_llm_available(),
    reason="requires LLM to run and doesn't work in Github Actions.",
)
def test_wikipedia_search_CZB():
    try:
        term = "CZ Biohub"

        # Get summary of wikipedia article:
        text = search_wikipedia(term, do_summarize=True)

        aprint(text)

        # Skip if search returned no results (flaky external dependency)
        if not text or text.strip() == "":
            pytest.skip("Wikipedia/DuckDuckGo search returned no results")

        assert "CZ Biohub" in text or "Biohub" in text or "Chan Zuckerberg" in text

    except DuckDuckGoSearchException as e:
        pytest.skip(f"DuckDuckGo search unavailable: {e}")
