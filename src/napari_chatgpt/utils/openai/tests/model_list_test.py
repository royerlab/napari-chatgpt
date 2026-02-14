import pytest

from napari_chatgpt.llm.litemind_api import is_llm_available
from napari_chatgpt.utils.openai.model_list import get_openai_model_list


@pytest.mark.skipif(not is_llm_available(), reason="requires LLM to run")
def test_model_list():
    model_list = get_openai_model_list()
    assert model_list and len(model_list) > 0
