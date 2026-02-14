import pytest
from arbol import aprint

from napari_chatgpt.llm.litemind_api import is_llm_available
from napari_chatgpt.utils.llm.summarizer import summarize
from napari_chatgpt.utils.web.scrapper import text_from_url


@pytest.mark.skipif(not is_llm_available(), reason="requires LLM to run")
def test_summarizer():
    url = "https://en.wikipedia.org/wiki/Albert_Einstein"

    # Download text:
    text = text_from_url(url)

    # limit text length:
    text = text[:4000]

    # Summarise text:
    summary = summarize(text)

    aprint(summary)

    assert len(summary) > 0
    assert "Einstein" in summary or "physicist" in summary
