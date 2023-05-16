import pytest
from arbol import aprint

from napari_chatgpt.utils.api_keys.api_key import is_api_key_available
from napari_chatgpt.utils.llm.summarizer import summarize
from napari_chatgpt.utils.web.scrapper import text_from_url


@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_summarizer():
    url = 'https://en.wikipedia.org/wiki/Albert_Einstein'

    # Download text:
    text = text_from_url(url)

    # limit text length:
    text = text[:4000]

    # Summarise text:
    summary = summarize(text)

    aprint(summary)

    assert len(text) > 0
    assert 'Einstein' in text
