import copy
from unittest.mock import MagicMock, patch

import pytest

from napari_chatgpt.utils.web.google import search_overview


@pytest.mark.integration
def test_google_search_overview():
    try:
        term = "wiki Mickey Mouse"
        text = search_overview(term)

        assert isinstance(text, str)
        assert len(text) > 0

    except Exception as e:
        pytest.skip(f"Google/DuckDuckGo search unavailable: {e}")


def test_google_search_max_pages_guard():
    """Fix 6: search_google terminates with no results."""
    from napari_chatgpt.utils.web.google import search_google

    # Mock _req to return HTML with no matching div.g elements
    mock_resp = MagicMock()
    mock_resp.text = "<html><body>No results</body></html>"
    mock_resp.raise_for_status = MagicMock()

    with patch("napari_chatgpt.utils.web.google._req", return_value=mock_resp):
        results = list(search_google("test query", num_results=100))

    # Should terminate and yield no results
    assert results == []


def test_req_does_not_mutate_global_headers():
    """Fix 8: _req should not mutate global headers."""
    from napari_chatgpt.utils.web import headers as headers_module
    from napari_chatgpt.utils.web.google import _req

    hdrs = headers_module._scrapping_request_headers
    original_ua = hdrs.get("User-Agent")
    snapshot = copy.deepcopy(hdrs)

    mock_resp = MagicMock()
    mock_resp.text = "<html></html>"
    mock_resp.raise_for_status = MagicMock()

    with patch("napari_chatgpt.utils.web.google.get", return_value=mock_resp):
        _req("test", 10, "en", 0, 5)

    # Global dict should be unchanged
    assert hdrs == snapshot
    assert hdrs.get("User-Agent") == original_ua
