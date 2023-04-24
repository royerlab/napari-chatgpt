from arbol import aprint

from src.napari_chatgpt.utils.wikipedia import search_wikipedia


def test_wikipedia_search():
    term = 'Albert Einstein'

    # Get summary of wikipedia article:
    text = search_wikipedia(term,
                            summarise_page=True)

    aprint(text)
