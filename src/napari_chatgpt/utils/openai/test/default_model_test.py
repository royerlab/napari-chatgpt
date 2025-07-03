import pytest

from napari_chatgpt.llm.litemind_api import is_available
from napari_chatgpt.utils.openai.default_model import get_default_openai_model_name


@pytest.mark.skipif(not is_available(), reason="requires LLM to run")
def test_default_model():
    assert (
        "gpt-3" in get_default_openai_model_name()
        or "gpt-4" in get_default_openai_model_name()
    )
