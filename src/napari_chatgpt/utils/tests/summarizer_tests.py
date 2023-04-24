from arbol import aprint

from src.napari_chatgpt.utils.scrapper import text_from_url
from src.napari_chatgpt.utils.summarizer import summarize


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
