from arbol import aprint
from ddgs.exceptions import RatelimitException

from napari_chatgpt.utils.web.google import search_overview


def test_google_search_overview():
    try:
        term = "wiki Mickey Mouse"
        text = search_overview(term)

        aprint(text)

    except RatelimitException as e:
        aprint(f"RatelimitException: {e}")
        import traceback

        traceback.print_exc()
