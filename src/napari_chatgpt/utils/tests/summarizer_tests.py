import pytest
from arbol import aprint

from napari_chatgpt.utils.openai_key import is_openai_key_available
from src.napari_chatgpt.utils.scrapper import text_from_url
from src.napari_chatgpt.utils.summarizer import summarize

@pytest.mark.skipif(not is_openai_key_available(), reason="requires OpenAI key to run")
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
    assert 'Albert Einstein' in text
