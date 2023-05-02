import pytest
from arbol import aprint

from napari_chatgpt.utils.duckduckgo import summary_ddg
from napari_chatgpt.utils.openai_key import is_openai_key_available


@pytest.mark.skipif(not is_openai_key_available(), reason="requires OpenAI key to run")
def test_duckduckgo_search_overview():
    term = 'wiki Mickey Mouse'
    text = summary_ddg(term)

    aprint(text)
