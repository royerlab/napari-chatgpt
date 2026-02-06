import pytest

from napari_chatgpt.llm.litemind_api import is_llm_available
from napari_chatgpt.utils.openai.default_model import get_default_openai_model_name


@pytest.mark.skipif(not is_llm_available(), reason="requires LLM to run")
def test_default_model():
    model_name = get_default_openai_model_name()
    # Check that the model name is a valid GPT model (gpt-3, gpt-4, gpt-5, etc.)
    assert model_name is not None
    assert model_name.startswith("gpt-")
