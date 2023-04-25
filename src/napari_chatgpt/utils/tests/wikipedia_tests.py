from arbol import aprint

from src.napari_chatgpt.utils.wikipedia import search_wikipedia


def test_wikipedia_search_1():
    term = 'Albert Einstein'

    # Get summary of wikipedia article:
    text = search_wikipedia(term,
                            do_summarize=True)

    aprint(text)

def test_wikipedia_search_2():
    term = 'CZ Biohub'

    # Get summary of wikipedia article:
    text = search_wikipedia(term,
                            do_summarize=True)

    aprint(text)
