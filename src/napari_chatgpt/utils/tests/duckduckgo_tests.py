from arbol import aprint

from napari_chatgpt.utils.duckduckgo import search_overview


def test_duckduckgo_search_overview():
    term = 'wiki Mickey Mouse'
    text = search_overview(term)

    aprint(text)
