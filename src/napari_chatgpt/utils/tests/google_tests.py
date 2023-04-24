from arbol import aprint

from src.napari_chatgpt.utils.google import search_overview


def test_google_search_overview():
    term = 'wiki Mickey Mouse'
    text = search_overview(term)

    aprint(text)
