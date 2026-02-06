"""Tests for wikipedia search - both mocked and integration."""

import os
from unittest.mock import patch

import pytest
from duckduckgo_search.exceptions import DuckDuckGoSearchException

from napari_chatgpt.llm.litemind_api import is_llm_available
from napari_chatgpt.utils.web.wikipedia import search_wikipedia

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


# --- Integration tests ---


@pytest.mark.integration
@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions.")
def test_wikipedia_search_MM():
    try:
        text = search_wikipedia("Mickey Mouse", do_summarize=False)

        if not text or text.strip() == "":
            pytest.skip("Wikipedia/DuckDuckGo search returned no results")

        assert "Mickey Mouse" in text or "Mickey" in text

    except DuckDuckGoSearchException as e:
        pytest.skip(f"DuckDuckGo search unavailable: {e}")


@pytest.mark.integration
@pytest.mark.skipif(
    IN_GITHUB_ACTIONS or not is_llm_available(),
    reason="requires LLM to run and doesn't work in Github Actions.",
)
def test_wikipedia_search_AE():
    try:
        text = search_wikipedia("Albert Einstein", do_summarize=True)

        if not text or text.strip() == "":
            pytest.skip("Wikipedia/DuckDuckGo search returned no results")

        assert "Albert Einstein" in text or "Einstein" in text

    except DuckDuckGoSearchException as e:
        pytest.skip(f"DuckDuckGo search unavailable: {e}")


@pytest.mark.integration
@pytest.mark.skipif(
    IN_GITHUB_ACTIONS or not is_llm_available(),
    reason="requires LLM to run and doesn't work in Github Actions.",
)
def test_wikipedia_search_CZB():
    try:
        text = search_wikipedia("CZ Biohub", do_summarize=True)

        if not text or text.strip() == "":
            pytest.skip("Wikipedia/DuckDuckGo search returned no results")

        assert "CZ Biohub" in text or "Biohub" in text or "Chan Zuckerberg" in text

    except DuckDuckGoSearchException as e:
        pytest.skip(f"DuckDuckGo search unavailable: {e}")


# --- Mocked unit tests ---


@patch("napari_chatgpt.utils.web.wikipedia.search_ddg")
def test_wikipedia_mocked_results(mock_search):
    mock_search.return_value = [
        {"body": "Mickey Mouse is a cartoon character."},
        {"body": "Created by Walt Disney and Ub Iwerks."},
        {"body": "First appeared in 1928."},
    ]

    text = search_wikipedia("Mickey Mouse", num_results=3, do_summarize=False)

    assert "Mickey Mouse is a cartoon character" in text
    assert "Walt Disney" in text


@patch("napari_chatgpt.utils.web.wikipedia.search_ddg")
def test_wikipedia_max_text_length(mock_search):
    mock_search.return_value = [
        {"body": "A" * 5000},
    ]

    text = search_wikipedia("test", max_text_length=100, do_summarize=False)

    assert len(text) <= 100


@patch("napari_chatgpt.utils.web.wikipedia.search_ddg")
def test_wikipedia_num_results_clamping(mock_search):
    mock_search.return_value = [{"body": f"Result {i}"} for i in range(15)]

    search_wikipedia("test", num_results=15, do_summarize=False)

    # search_ddg should be called with min(10, 15) = 10
    call_kwargs = mock_search.call_args
    assert (
        call_kwargs[1]["num_results"] == 10
        or call_kwargs.kwargs.get("num_results") == 10
    )


@patch("napari_chatgpt.utils.web.wikipedia.search_ddg")
def test_wikipedia_empty_results(mock_search):
    mock_search.return_value = []

    text = search_wikipedia("test", do_summarize=False)

    assert text == ""
