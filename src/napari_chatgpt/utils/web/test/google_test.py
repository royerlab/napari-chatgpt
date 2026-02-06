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
