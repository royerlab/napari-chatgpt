"""Tests for duckduckgo search functions - both mocked and integration."""

from unittest.mock import MagicMock, patch

import pytest
from duckduckgo_search.exceptions import DuckDuckGoSearchException

from napari_chatgpt.llm.litemind_api import is_llm_available
from napari_chatgpt.utils.web.duckduckgo import search_ddg, summary_ddg

# --- Integration tests ---


@pytest.mark.integration
@pytest.mark.skipif(not is_llm_available(), reason="requires LLM to run")
def test_duckduckgo_search_overview_summary():
    try:
        query = "Mickey Mouse"
        text = summary_ddg(query, do_summarize=True)
        if "Web search failed" in text or text == "No results.":
            pytest.skip("DuckDuckGo search rate limited or unavailable")
        assert "Mickey" in text

    except DuckDuckGoSearchException as e:
        pytest.skip(f"DuckDuckGo search unavailable: {e}")


@pytest.mark.integration
def test_duckduckgo_search_overview():
    try:
        query = "Mickey Mouse"
        text = summary_ddg(query, do_summarize=False)
        if "Web search failed" in text or text == "No results.":
            pytest.skip("DuckDuckGo search rate limited or unavailable")
        assert "Mickey" in text

    except DuckDuckGoSearchException as e:
        pytest.skip(f"DuckDuckGo search unavailable: {e}")


# --- Mocked unit tests ---


@patch("napari_chatgpt.utils.web.duckduckgo.DDGS")
def test_search_ddg_returns_results(mock_ddgs_class):
    mock_instance = MagicMock()
    mock_ddgs_class.return_value = mock_instance
    mock_instance.text.return_value = [
        {"title": "Result 1", "body": "Body 1", "href": "http://example.com/1"},
        {"title": "Result 2", "body": "Body 2", "href": "http://example.com/2"},
    ]

    results = search_ddg("test query", num_results=2)

    assert len(results) == 2
    assert results[0]["title"] == "Result 1"
    mock_instance.text.assert_called_once()


@patch("napari_chatgpt.utils.web.duckduckgo.DDGS")
def test_search_ddg_returns_none(mock_ddgs_class):
    mock_instance = MagicMock()
    mock_ddgs_class.return_value = mock_instance
    mock_instance.text.return_value = None

    results = search_ddg("test query")

    assert results == []


@patch("napari_chatgpt.utils.web.duckduckgo.DDGS")
def test_search_ddg_returns_empty(mock_ddgs_class):
    mock_instance = MagicMock()
    mock_ddgs_class.return_value = mock_instance
    mock_instance.text.return_value = []

    results = search_ddg("test query")

    assert results == []


@patch("napari_chatgpt.utils.web.duckduckgo.DDGS")
def test_search_ddg_lang_conversion(mock_ddgs_class):
    mock_instance = MagicMock()
    mock_ddgs_class.return_value = mock_instance
    mock_instance.text.return_value = []

    search_ddg("test", lang="en")

    mock_instance.text.assert_called_once_with(
        keywords="test", region="en-us", safesearch="moderate", max_results=3
    )


@patch("napari_chatgpt.utils.web.duckduckgo.search_ddg")
def test_summary_ddg_exception_path(mock_search):
    mock_search.side_effect = Exception("network error")

    result = summary_ddg("test query", do_summarize=False)

    assert "Web search failed for: 'test query'" in result


@patch("napari_chatgpt.utils.web.duckduckgo.search_ddg")
def test_summary_ddg_empty_results(mock_search):
    mock_search.return_value = []

    result = summary_ddg("test query", do_summarize=False)

    assert result == "No results."


@patch("napari_chatgpt.utils.web.duckduckgo.search_ddg")
def test_summary_ddg_with_results_no_summarize(mock_search):
    mock_search.return_value = [
        {"title": "Mickey", "body": "A famous mouse", "href": "http://example.com"},
    ]

    result = summary_ddg("Mickey Mouse", do_summarize=False)

    assert "Mickey" in result
    assert "famous mouse" in result
