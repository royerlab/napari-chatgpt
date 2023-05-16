from arbol import aprint

from napari_chatgpt.utils.web.google import search_overview


def test_google_search_overview():
    term = 'wiki Mickey Mouse'
    text = search_overview(term)

    aprint(text)
