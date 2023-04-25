from arbol import aprint

from napari_chatgpt.utils.duckduckgo import summary_ddg


def test_duckduckgo_search_overview():
    term = 'wiki Mickey Mouse'
    text = summary_ddg(term)

    aprint(text)
